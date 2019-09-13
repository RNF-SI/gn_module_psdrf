from flask import Blueprint, request, jsonify
from sqlalchemy.orm import subqueryload, joinedload
from sqlalchemy.sql import func
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import MultiPoint, Point

from geonature.utils.env import DB
from geonature.utils.utilssqlalchemy import json_resp, get_geojson_feature
from .models import TDispositifs, TPlacettes, TArbres

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

    query = DB.session.query(TDispositifs).outerjoin(TDispositifs.placettes) \
        .group_by(TDispositifs) \
        .having(func.count(TDispositifs.placettes) > 0) \
        .order_by(TDispositifs.name)
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
        ft['properties'] = {
            'name': pg.name,
            'id_dispositif': pg.id_dispositif,
            'rights': {'C': False, 'R': True, 'U': False, 'V': True, 'E': False, 'D': False},
            'leaflet_popup': pg.name
        }
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
    pass


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