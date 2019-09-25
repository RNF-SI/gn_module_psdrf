import datetime

from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import subqueryload, joinedload
from sqlalchemy.sql import func, distinct
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import MultiPoint, Point

from geonature.utils.env import DB
from geonature.utils.utilssqlalchemy import json_resp, get_geojson_feature
from geonature.core.ref_geo.models import LiMunicipalities, LAreas, BibAreasTypes
from geonature.core.gn_permissions.tools import get_or_fetch_user_cruved
from geonature.core.gn_permissions import decorators as permissions
from pypnusershub.routes import check_auth
from .models import TDispositifs, TPlacettes, TArbres, TCycles, \
    CorCyclesPlacettes, TArbresMesures, BibEssences


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
    except (ValueError, TypeError):
        status = None

    query = DB.session.query(TDispositifs) \
        .options(joinedload(TDispositifs.placettes), joinedload(TDispositifs.cycles)) \
        .filter(TDispositifs.cycles.any(TCycles.date_debut < datetime.datetime.today())) \
        .order_by(TDispositifs.name)

    if alluvial is not None and alluvial != '':
        if alluvial.lower() == 'true':
            where = TCycles.monitor != 'PSDRF'
        elif alluvial.lower() == 'false':
            where = TCycles.monitor == 'PSDRF'
        else:
            alluvial = None
        if alluvial is not None:
            query = query.filter(TDispositifs.cycles.any(where))

    if region and region != 'null':
        query = query.filter(TDispositifs.municipalities.any(LiMunicipalities.insee_reg == region))

    if status:
        query = query.filter(TDispositifs.areas.any(LAreas.id_type == status))

    total = query.count()
    pgs = query.offset(page * limit).limit(limit).all()
    items = []

    # rassemble les geom des placettes pour en former l'enveloppe
    for pg in pgs:
        pts = MultiPoint([to_shape(pl.geom_wgs84) for pl in pg.placettes if pl.geom_wgs84 is not None])
        if shape == "point":
            geom = pts.centroid
        else:
            geom = pts.convex_hull
        if len(pts) > 0:
            ft = get_geojson_feature(from_shape(geom))
        else:
            ft = {'geometry': None}

        cycle_1 = None
        if len(pg.cycles) > 0:
            cycle_1 = [c for c in pg.cycles if c.num_cycle == 1][0]

        ft['properties'] = {
            'name': pg.name,
            'id_dispositif': pg.id_dispositif,
            'nb_placettes': len(pg.placettes),
            'cycle': max([c.num_cycle for c in pg.cycles]),
            'rights': {'C': False, 'R': True, 'U': False, 'V': True, 'E': False, 'D': False},
            'leaflet_popup': pg.name
        }
        if cycle_1 and cycle_1.date_debut:
            ft['properties']['debut'] = cycle_1.date_debut.year
        ft['id'] = pg.id_dispositif
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
@permissions.check_cruved_scope('R', True, module_code="PSDRF")
@json_resp
def get_dispositif(id_dispositif, info_role):
    disp = DB.session.query(TDispositifs) \
        .options(joinedload(TDispositifs.organisme)) \
        .filter(TDispositifs.id_dispositif == id_dispositif).one()
    organisme = None
    if disp.organisme:
        organisme = {
            "nom_organisme": disp.organisme.nom_organisme,
            "id_organisme": disp.organisme.id_organisme
        }

    query = DB.session.query(TPlacettes.strate, func.count("*").label("cnt")) \
        .outerjoin(TArbres) \
        .filter(TPlacettes.id_dispositif == id_dispositif) \
        .group_by(TPlacettes.strate) \
        .order_by(TPlacettes.strate)

    strates = [{"strate": s.strate, "nb": s.cnt} for s in query.all()]

    user_cruved = get_or_fetch_user_cruved(session=session, id_role=info_role.id_role, module_code="PSDRF")

    return {
        "name": disp.name,
        "id": disp.id_dispositif,
        "organisme": organisme,
        "strates": strates,
        "cruved": user_cruved
        }


@blueprint.route('/saveDispositif', methods=['POST'])
@permissions.check_cruved_scope('U', True, module_code="PSDRF")
@json_resp
def save_dispositif(info_role):
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
        .filter(TDispositifs.cycles.any(TCycles.date_debut < datetime.datetime.today()))
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
    limit = int(request.args.get("limit", 1000))
    page = int(request.args.get("offset", 0))

    query = DB.session.query(TPlacettes) \
        .filter(TPlacettes.id_dispositif == id_dispositif) \
        .options(joinedload(TPlacettes.arbres)) \
        .order_by(TPlacettes.id_placette)
    total = query.count()
    query = query.offset(page * limit).limit(limit)

    data = {
        "total": total,
        "total_filtered": total,
        "page": page,
        "limit": limit,
        "items": {"type": "FeatureCollection", "features": []}
    }
    for pg in query.all():
        cnt = len(pg.arbres)
        ft = pg.as_geofeature('geom_wgs84', 'id_placette')
        ft["properties"]["nb_arbres"] = cnt
        ft["properties"]["rights"] =  {'C': False, 'R': True, 'U': False, 'V': False, 'E': False, 'D': False}
        ft["id"] = ft["properties"]["id_placette"]
        data["items"]["features"].append(ft)

    return data


@blueprint.route('/arbres/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_arbres(id_dispositif):
    """ Recherche tous les arbres d'un dispositif donné """
    pgs = DB.session.query(TArbres, TArbresMesures) \
        .filter(TArbresMesures.id_arbre == TArbres.id_arbre) \
        .filter(TArbres.placette.has(TPlacettes.id_dispositif == id_dispositif)) \
        .limit(5000).all()
    data = []
    for arbre, mesure in pgs:
        li = arbre.as_dict()
        li.update(mesure.as_dict())
        data.append(li)

    return {"items": data, "total":len(data)}
