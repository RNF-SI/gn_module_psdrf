from flask import Blueprint, request
from sqlalchemy.orm import subqueryload
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import MultiPoint

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
    limit = int(request.args.get("limit", 100))
    page = int(request.args.get("offset", 0))

    query = DB.session.query(TDispositifs).options(subqueryload(TDispositifs.placettes)) \
        .order_by(TDispositifs.name)
    total = query.count()
    pgs = query.offset(page * limit).limit(limit).all()
    items = []

    # rassemble les geom des placettes pour en former l'enveloppe
    for pg in pgs:
        pts = MultiPoint([to_shape(pl.geom_wgs84) for pl in pg.placettes if pl.geom_wgs84 is not None])
        ft = get_geojson_feature(from_shape(pts.convex_hull))
        ft['properties'] = {
            'name': pg.name,
            'id_dispositif': pg.id_dispositif,
            'rights': {},
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


@blueprint.route('/placettes/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_placettes(id_dispositif):
    pgs = DB.session.query(TPlacettes).filter(TPlacettes.id_dispositif == id_dispositif).all()
    return [pg.as_geofeature('geom', 'id_placette') for pg in pgs]


@blueprint.route('/arbres/<int:id_dispositif>', methods=['GET'])
@json_resp
def get_arbres(id_dispositif):
    """ Recherche tous les arbres d'un dispositif donné """
    pgs = DB.session.query(TArbres).filter(TArbres.placette.id_dispositif == id_dispositif).all()
    return [pg.as_dict() for pg in pgs]