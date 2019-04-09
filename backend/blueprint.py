from flask import Blueprint

from geonature.utils.env import DB
from geonature.utils.utilssqlalchemy import json_resp
from .models import TDispositifs, TPlacettes, TArbres

blueprint = Blueprint('psdrf', __name__)

@blueprint.route('/test', methods=['GET', 'POST'])
def test():
    return 'It works (ça marche !)'

@blueprint.route('/dispositifs', methods=['GET'])
@json_resp
def get_disps():
    pgs = DB.session.query(TDispositifs).all()
    return [pg.as_dict() for pg in pgs]


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