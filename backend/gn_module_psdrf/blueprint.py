from flask import Blueprint, request, make_response, send_file, send_from_directory, Response, jsonify
from sqlalchemy.orm import subqueryload, joinedload
from sqlalchemy.sql import func, distinct
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import false

from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import MultiPoint, Point
import json
import zipfile
from io import BytesIO
import time
import os
import logging

from geonature.utils.env import DB
# from geonature.utils.utilssqlalchemy import json_resp, get_geojson_feature

from geonature.core.users.models import CorRole
from pypnusershub.db.models import Organisme as BibOrganismes
from pypnusershub.db.models import User
from ref_geo.models import LiMunicipalities, LAreas, BibAreasTypes
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, CorDispositifsRoles, TBmSup30, TBmSup30Mesures, BibEssences
from .data_verification import data_verification
from .data_integration import data_integration
from .psdrf_list_update import psdrf_list_update
from .data_analysis import data_analysis
from .bddToExcel import bddToExcel
from .schemas.dispositifs import DispositifSchema
from .schemas.cycles import ConciseCycleSchema
from .schemas.essences import EssenceSchema


from utils_flask_sqla.response import json_resp
from utils_flask_sqla_geo.generic import get_geojson_feature

blueprint = Blueprint('psdrf', __name__)

@blueprint.route('/test', methods=['GET', 'POST'])
def test():
    return 'It works (ça marche !)'


@blueprint.route('/dispositifs', methods=['GET'])
@json_resp
def get_disps():
    """
        Retourne tous les dispositifs avec leur géométrie.
        Ne renvoie que les dispositifs ayant des placettes enregistrées
        Paramètres :
            :limit: nombre de résultats
            :offset: décalage
            :shape: 'point' pour le centroïde des placettes, 'polygon' pour l'enveloppe des placettes
    """
    limit = int(request.args.get("limit", 500))
    page = int(request.args.get("offset", 0))
    shape = request.args.get("shape", "point")

    region = request.args.get("region")
    alluvial = request.args.get("alluvial")
    try:
        status = int(request.args.get("status"))
    except ValueError:
        status = None

    query = DB.session.query(TDispositifs, func.max(TCycles.num_cycle).label("cycle")) \
        .outerjoin(TDispositifs.placettes) \
        .outerjoin(CorCyclesPlacettes) \
        .outerjoin(TCycles) \
        .group_by(TDispositifs) \
        .having(func.count(TDispositifs.placettes) > 0) \
        .order_by(TDispositifs.name)

    if alluvial is not None and alluvial != '':
        if alluvial.lower() == 'true':
            alluvial = True
        elif alluvial.lower() == 'false':
            alluvial = False
        else:
            alluvial = None
        if alluvial is not None:
            query = query.filter(TDispositifs.alluvial == alluvial)

    if region and region != 'null':
        query = query.filter(TDispositifs.municipalities.any(LiMunicipalities.insee_reg == region))

    if status:
        query = query.filter(TDispositifs.areas.any(LAreas.id_type == status))

    total = query.count()
    pgs = query.offset(page * limit).limit(limit).all()
    items = []

    # rassemble les geom des placettes pour en former l'enveloppe
    for pg in pgs:
        pts = MultiPoint([to_shape(pl.geom_wgs84) for pl in pg.TDispositifs.placettes if pl.geom_wgs84 is not None])
        if shape == "point":
            geom = pts.centroid
        else:
            geom = pts.convex_hull
        if len(pts) > 0:
            ft = get_geojson_feature(from_shape(geom))
        else:
            ft = {'geometry': None}
        ft['properties'] = {
            'name': pg.TDispositifs.name,
            'id_dispositif': pg.TDispositifs.id_dispositif,
            'nb_placettes': len(pg.TDispositifs.placettes),
            'cycle': pg.cycle,
            'rights': {'C': False, 'R': True, 'U': False, 'V': True, 'E': False, 'D': False},
            'leaflet_popup': pg.TDispositifs.name
        }
        ft['id'] = pg.TDispositifs.id_dispositif
        items.append(ft)

    # TODO: check les droits

    data = {
        "total": total,
        "page": page,
        "total_filtered": total,
        "limit": limit,
        "items": {"type": "FeatureCollection", "features": items}
    }
    return data


@blueprint.route('/status_types', methods=['GET'])
@json_resp
def get_status_types():
    """ Renvoie les différents types d'organismes concernés """
    query = DB.session.query(BibAreasTypes).filter(
        TDispositifs.areas.any(LAreas.id_type == BibAreasTypes.id_type)
    ).order_by(BibAreasTypes.type_name)
    data = [{'id_type': pg.id_type, 'name': pg.type_name} for pg in query]
    return data


@blueprint.route('/dispositif/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_dispositif(id_dispositif):
    disp = DB.session.query(TDispositifs) \
        .options(joinedload(TDispositifs.organisme)) \
        .filter(TDispositifs.id_dispositif == id_dispositif).one()
    organisme = None
    if disp.organisme:
        organisme = {
            "nom_organisme": disp.organisme.nom_organisme,
            "id_organisme": disp.organisme.id_organisme
        }
    return {
        "name": disp.name,
        "id": disp.id_dispositif,
        "organisme": organisme
        }


@blueprint.route('/saveDispositif', methods=['POST'])
@json_resp
def save_dispositif():
    data = request.get_json()
    id_dispositif = int(data.get("id"))
    if id_dispositif:
        disp = DB.session.query(TDispositifs).filter(TDispositifs.id_dispositif == id_dispositif).one()
        disp.name = data.get("name")
        disp.id_organisme = data.get("id_organisme")
        DB.session.commit()
        return {"success": True}
    return {"success": False, "message": "Id was not provided in data."}


@blueprint.route('/global_stats', methods=['GET'])
@json_resp
def global_stats():
    """ Renvoie des chiffres globaux séparés par cycle """

    data = { }
    query = DB.session.query(func.count('*')).select_from(TDispositifs) \
        .filter(TDispositifs.placettes.any())
    data['nb_dispositifs'] = query.scalar()

    query = DB.session.query(
        TCycles.num_cycle,
        func.count(CorCyclesPlacettes.id_placette),
        func.count(distinct(TCycles.id_dispositif))) \
        .join(CorCyclesPlacettes) \
        .group_by(TCycles.num_cycle)
    data['cycles'] = {pg[0]: {'nb_placettes': pg[1], 'nb_dispositifs': pg[2]} for pg in query.all()}

    query = DB.session.query(
        TCycles.num_cycle,
        func.count(TArbresMesures.id_arbre_mesure)) \
        .join(TArbresMesures) \
        .group_by(TCycles.num_cycle)
    for pg in query.all():
        data['cycles'][pg[0]]['nb_arbres'] = pg[1]
    data['nb_cycles'] = len(data['cycles'])

    return data



@blueprint.route('/placettes/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_placettes(id_dispositif):
    limit = int(request.args.get("limit", 100))
    page = int(request.args.get("offset", 0))
    query = DB.session.query(TPlacettes).filter(TPlacettes.id_dispositif == id_dispositif).order_by(TPlacettes.id_placette)
    total = query.count()
    pgs = query.offset(page * limit).limit(limit).all()

    data = {
        "total": total,
        "total_filtered": total,
        "page": page,
        "limit": limit,
        "items": {"type": "FeatureCollection", "features": [pg.as_geofeature('geom_wgs84', 'id_placette') for pg in pgs]}
    }
    for ft in data["items"]["features"]:
        ft["properties"]["rights"] =  {'C': True, 'R': True, 'U': True, 'V': True, 'E': True, 'D': True}
        ft["id"] = ft["properties"]["id_placette"]

    return data


@blueprint.route('/arbres/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_arbres(id_dispositif):
    """ Recherche tous les arbres d'un dispositif donné """
    pgs = DB.session.query(TArbres).filter(TArbres.placette.id_dispositif == id_dispositif).all()
    return [pg.as_dict() for pg in pgs]

@blueprint.route('/validation', methods=['POST'])
@json_resp
def psdrf_data_verification():
    data = request.get_json()
    return data_verification(data)

@blueprint.route('/shapeValidation', methods=['POST'])
def psdrf_data_verification_with_shape():
    default_name = "None"
    shape_file = request.files.get('file', default_name)
    data=json.loads(request.files.get('overrides', default_name).read())
    data_verification(data)
    return "good"

@blueprint.route('/integration', methods=['POST'])
@json_resp
def psdrf_data_integration():
    dispId = request.form.get('dispositifId')
    dispName = request.form.get('dispositifName')
    default_name = "None"
    data = json.loads(request.files.get('psdrfData', default_name).read())
    return data_integration(dispId, dispName, data)


@blueprint.route('/analysis/<int:id_dispositif>', methods=['GET'])
def psdrf_data_analysis(id_dispositif):

    isCarnetToDownload = request.args.get('isCarnetToDownload')
    carnetToDownloadParameters = {}
    if isCarnetToDownload:
        carnetToDownloadParameters['Answer_Radar']= request.args.get('Answer_Radar')
    else:
        carnetToDownloadParameters['Answer_Radar']=None

    isPlanDesArbresToDownload = request.args.get('isPlanDesArbresToDownload')

    outFilePath = "/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/out/"
    try:
        data_analysis(str(id_dispositif), isCarnetToDownload, isPlanDesArbresToDownload, carnetToDownloadParameters)
    except Exception as e:
        logging.critical(e)
        msg = json.dumps({"type": "bug", "msg": "Unkown error during analysis"})
        logging.info(msg)
        return Response(msg, status=500)

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:

        for dirname, subdirs, files in os.walk(outFilePath):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(outFilePath) :]
                if (arcname != '.gitignore') and (not arcname.endswith(('.log', '.tex'))):
                    zf.write(absname, arcname)

    memory_file.seek(0)

    zipName = 'documents_dispositif-'+str(id_dispositif)+'.zip'

    result = send_file(
        memory_file, 
        mimetype = 'zip',
        download_name= zipName,
        as_attachment=True
        )

    response = make_response(result)
    response.headers["filename"]=zipName
    response.headers['Access-Control-Expose-Headers'] = 'filename'   
    try:
        return response
    except FileNotFoundError:
        abort(404)

@blueprint.route('/dispositifsList', methods=['GET'])
@json_resp
def get_disp_list():
    """
        Retourne tous les dispositifs avec id et nom
    """
    query = DB.session.query(
        TDispositifs.id_dispositif, TDispositifs.name, TDispositifs.id_organisme, TDispositifs.alluvial, BibOrganismes.nom_organisme
        ).outerjoin(
            BibOrganismes, BibOrganismes.id_organisme == TDispositifs.id_organisme
        ).all() 
    data = [{'id_dispositif':disp.id_dispositif, 'alluvial': disp.alluvial, 'nom_dispositif': disp.name, "id_organisme": disp.id_organisme, "nom_organisme": disp.nom_organisme} for disp in query]
    return data

@blueprint.route('/groupList/<int:userId>', methods=['GET'])
@json_resp
def getUserGroups(userId):
    """
        Retourne tous les groupes pour un utilisateur ID
    """     
    query = DB.session.query(
        CorRole      
    ).filter(
        CorRole.id_role_utilisateur == userId
    ).all()
    data = [group.id_role_groupe for group in query]
    return data


@blueprint.route('/corDispositifRole', methods=['POST', 'PUT', 'DELETE'])
@json_resp
def add_cor_disp_role():
    data = request.get_json()
    if request.method == 'POST':
        new_cor_disp_role = CorDispositifsRoles(
            id_dispositif = data["dispositif"],
            id_role= data["utilisateur"],
        )
        try:
            DB.session.add(new_cor_disp_role)
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'PUT':
        dispRole = CorDispositifsRoles.query.filter_by(
            id_dispositif=data["dispositif"], 
            id_role=data["utilisateur"]
        ).first()
        dispRole.id_dispositif=""
        dispRole.id_role=""
        try:
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'DELETE':
        try:
            CorDispositifsRoles.query.filter_by(
                id_dispositif=data["id_dispositif"], 
                id_role=data["id_role"]
            ).delete()
            DB.session.commit()
            return {"success": "Suppression validés"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

@blueprint.route('/userDisps/<int:userId>', methods=['GET'])
@json_resp
def get_user_disps(userId):
    query = DB.session.query(CorDispositifsRoles).filter(
            CorDispositifsRoles.id_role == userId
        ).all()
    data = [disp.id_dispositif for disp in query]
    return data

@blueprint.route('/excelData/<int:dispId>', methods=['GET'])
@json_resp
def get_excel_data(dispId):
    data = bddToExcel(dispId)
    return data

@blueprint.route('/organisme', methods=['POST', 'PUT', 'DELETE'])
@json_resp
def postOrganisme():
    data = request.get_json()
    print(data)
    if request.method == 'POST':
        new_organisme = BibOrganismes(
            nom_organisme = data["newOrganisme"],
            adresse_organisme = data["adresseOrga"],
            cp_organisme = data["cpOrga"],
            ville_organisme = data["villeOrga"],
            tel_organisme = data["telOrga"],
            email_organisme = data["mailOrga"]
        )
        try:
            DB.session.add(new_organisme)
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'PUT':
        try:
            orga = BibOrganismes.query.filter_by(
                id_organisme = data["id_organisme"]
            ).first()
            orga.nom_organisme = data["newOrganisme"],
            orga.adresse_organisme = data["adresseOrga"],
            orga.cp_organisme = data["cpOrga"],
            orga.ville_organisme = data["villeOrga"],
            orga.tel_organisme = data["telOrga"],
            orga.email_organisme = data["mailOrga"]
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'DELETE':
        try:
            BibOrganismes.query.filter_by(
                id_organisme =data["id_organisme"]
            ).delete()
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error

@blueprint.route('/listOrganism', methods=['GET'])
@json_resp
def get_list_organism():
    query = DB.session.query(BibOrganismes.id_organisme, BibOrganismes.nom_organisme, BibOrganismes.adresse_organisme, BibOrganismes.ville_organisme, BibOrganismes.cp_organisme, BibOrganismes.tel_organisme, BibOrganismes.email_organisme).all()
    data = [{'id':organisme.id_organisme, 'nom_organisme': organisme.nom_organisme, 'adresse_organisme': organisme.adresse_organisme, 'ville_organisme': organisme.ville_organisme, 'cp_organisme': organisme.cp_organisme, "telephone_organisme": organisme.tel_organisme, "email_organisme": organisme.email_organisme} for organisme in query]
    return data

@blueprint.route('/dispositif', methods=['POST', "DELETE", "PUT"])
@json_resp
def postDispositif():
    data = request.get_json()
    print(data)
    if request.method == 'POST':
        new_dispositif = TDispositifs(
            id_dispositif = data["idDispositif"],
            name = data["newDispositif"],
            id_organisme = data["dispOrganisme"],
            alluvial = data["alluvial"]
        )
        try:
            DB.session.add(new_dispositif)
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'DELETE':
        try:
            TDispositifs.query.filter_by(
                id_dispositif =data["id_dispositif"]
            ).delete()
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error
    if request.method == 'PUT':
        try:
            disp = TDispositifs.query.filter_by(
                id_dispositif =data["id_dispositif"]
            ).first()
            disp.id_dispositif = data["idDispositif"],
            disp.name = data["newDispositif"],
            disp.id_organisme = data["dispOrganisme"],
            disp.alluvial = data["alluvial"]
            print(disp)
            DB.session.commit()
            return {"success": "Ajout validé"}
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return error





@blueprint.route('/corDispositifRole', methods=['GET'])
@json_resp
def get_corDispositifRole():
    query = DB.session.query(
        CorDispositifsRoles.id_dispositif, CorDispositifsRoles.id_role, TDispositifs.name, User.prenom_role, User.nom_role
    ).join(
        TDispositifs, TDispositifs.id_dispositif == CorDispositifsRoles.id_dispositif
    ).join(
        User, User.id_role == CorDispositifsRoles.id_role
    ).all()
    data = [{'id_utilisateur': userDisp.id_role, 'nom_utilisateur':userDisp.nom_role, 'prenom_utilisateur': userDisp.prenom_role, 'id_dispositif': userDisp.id_dispositif, 'nom_dispositif': userDisp.name} for userDisp in query]
    return data

@blueprint.route('/users', methods=['GET'])
@json_resp
def get_Users():
    """
        Retourne tous les utilisateurs (sans les groupes)
    """     
    query = DB.session.query(
        User.id_role, User.groupe, User.id_organisme, User.prenom_role, User.nom_role, User.email, User.identifiant, User.remarques, BibOrganismes.nom_organisme
    ).filter(
        User.groupe == False
    ).outerjoin(
        BibOrganismes, BibOrganismes.id_organisme == User.id_organisme
    ).all()
    data = [{'id_utilisateur': user.id_role, 'nom_utilisateur':user.nom_role, 'prenom_utilisateur': user.prenom_role, 'email_utilisateur': user.email, 'identifiant_utilisateur': user.identifiant, 'id_organisme': user.id_organisme, 'nom_organisme': user.nom_organisme, 'remarques_utilisateur': user.remarques} for user in query]
    print(data)
    return data


@blueprint.route('/groups', methods=['GET'])
@json_resp
def get_Groups():
    """
        Retourne tous les groupes (sans les utilisateurs)
    """     
    query = DB.session.query(
        User.id_role, User.groupe, User.prenom_role, User.nom_role, User.identifiant
    ).filter(
        User.groupe == True
    ).all()
    data = [{'id_utilisateur': user.id_role, 'nom_utilisateur':user.nom_role, 'prenom_utilisateur': user.prenom_role, 'identifiant_utilisateur': user.identifiant} for user in query]
    return data
    

@blueprint.route('/psdrfListe', methods=['POST'])
@json_resp
def psdrf_update_psdrf_liste():
    psdrfListe_file = request.files.get('file_upload', 'psdrfListe')
    try:
        psdrf_list_update(psdrfListe_file)
        return {"success": True, "message": "Les données administrateurs ont bien été mises à jour."}
    except Exception as e:
        logging.critical(e)
        msg = json.dumps({"type": "bug", "msg": "Unknown error during psdrf liste change"})
        logging.info(msg)
        return Response(msg, status=500)


# Fonctions pour l'application de saisir PSDRF

@blueprint.route('/user-dispositif-list/<int:userId>', methods=['GET'])
@json_resp
def get_user_dispositif_list(userId):
    query = DB.session.query(
        TDispositifs.id_dispositif, TDispositifs.name, TDispositifs.id_organisme, TDispositifs.alluvial, CorDispositifsRoles.id_role
    ).join(
        TDispositifs, TDispositifs.id_dispositif == CorDispositifsRoles.id_dispositif
    ).filter(
        CorDispositifsRoles.id_role == userId
    ).all()
    data = [{'id_dispositif': userDisp.id_dispositif, 'alluvial': userDisp.alluvial, 'name': userDisp.name, "id_organisme": userDisp.id_organisme} for userDisp in query]
    return data

@blueprint.route('/dispositif-complet/<int:id_dispositif>', methods=['GET'])
def get_dispositif_complet(id_dispositif):
    query = DB.session.query(
        TDispositifs
    ).filter(
        TDispositifs.id_dispositif == id_dispositif
    ).one()
    schema = DispositifSchema(many=False)
    Obj = schema.dump(query)
    return make_response(jsonify(Obj), 200)

@blueprint.route('/dispositif-cycles/<int:id_dispositif>', methods=['GET'])
def get_dispositif_cycles(id_dispositif):
    query = DB.session.query(
        TCycles
    ).filter(
        TCycles.id_dispositif == id_dispositif
    ).all()
    schema = ConciseCycleSchema(many=True)
    Obj = schema.dump(query)
    return make_response(jsonify(Obj), 200)

@blueprint.route('/essences', methods=['GET'])
def get_essences():
    query = DB.session.query(
        BibEssences
    ).all()
    schema = EssenceSchema(many=True)
    Obj = schema.dump(query)
    return make_response(jsonify(Obj), 200)

@blueprint.route('/bib_nomenclatures_types', methods=['GET'])
def get_PSDRF_bib_nomenclatures():
    try:
        bib_nomenclatures_types = DB.session.execute("""
            SELECT *
            FROM ref_nomenclatures.bib_nomenclatures_types
            WHERE source = 'PSDRF';
            """
        ).fetchall()
        return bib_nomenclatures_types
    except Exception:
        raise

@blueprint.route('/t_nomenclatures', methods=['GET'])
def get_PSDRF_t_nomenclatures():
    try:
        t_nomenclatures = DB.session.execute("""
            SELECT *
            FROM ref_nomenclatures.t_nomenclatures
            WHERE source = 'PSDRF';
            """
        ).fetchall()
        return t_nomenclatures
    except Exception:
        raise

    # query = DB.session.query(
    #     ref_nomenclatures.bib_nomenclatures_types
    # ).all()
    # # schema = EssenceSchema(many=True)
    # Obj = schema.dump(query)
    # return make_response(jsonify(Obj), 200)


# @blueprint.route('/arbres/<int:id_dispositif>', methods=['GET'])
# @json_resp
# def get_arbres(id_dispositif):
#     """ Recherche tous les arbres d'un dispositif donné """
#     pgs = DB.session.query(TArbres).filter(TArbres.placette.id_dispositif == id_dispositif).all()
#     return [pg.as_dict() for pg in pgs]