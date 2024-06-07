from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TDispositifsStaging
from geonature.utils.env import ma
from .placettes import PlacetteStagingSchema
from .cycles import CycleStagingSchema

class DispositifStagingSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TDispositifsStaging
        include_fk = True
    placettes = ma.Nested(PlacetteStagingSchema, exclude=('geom', 'geom_wgs84'), many = True)
    cycles = ma.Nested(CycleStagingSchema, many = True)

