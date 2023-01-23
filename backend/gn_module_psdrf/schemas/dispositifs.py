from flask_marshmallow import fields
from ..models import TDispositifs
from geonature.utils.env import ma
from .placettes import PlacetteSchema
from .cycles import CycleSchema

class DispositifSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TDispositifs
        include_fk = True
    placettes = ma.Nested(PlacetteSchema, exclude=('geom', 'geom_wgs84'), many = True)
    # placettes = ma.List(ma.Nested(PlacetteSchema, exclude=('dispositif', 'reperes', 'geom', 'arbres', 'bmsSup30', 'geom_wgs84'), many = True))
    # cycles = ma.List(ma.Nested(CycleSchema, exclude=('dispositif', 'corCyclesPlacettes'), many = True))
    cycles = ma.Nested(CycleSchema, many = True)
    # utilisateurs = ma.Nested(lambda :UserComplementSchema, many = True, only=['id_role','id_user','profil_opnl'])
    # ressources = ma.Nested(lambda :RessourcesSchema, many=True)
    # # ressources = ma.Nested(lambda :RessourcesSchema, many=True, exclude=('sites',))
    # sous_sites = ma.Nested('self', many = True, only=['id_site', 'nom_site','description','projets'])
    # site_fonc = ma.Nested('self', many = True, only=['id_site', 'nom_site'])
    # actualites = ma.List(ma.Nested("ActualitesSchema", exclude=("sites", "projets", "ressources")))
    # evenements = ma.List(ma.Nested("EvenementSchema", exclude=("sites", "projets", "ressources")))
    # projets = ma.List(ma.Nested("ThematiqueSchema", exclude=("sites", "ressources", "actualites", "utilisateurs", "ateliers")))
    # emplois = ma.List(ma.Nested("EmploisSchema", exclude=("sites", "ressources", "projets")))
