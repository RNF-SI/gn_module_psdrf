from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TCyclesStaging
from geonature.utils.env import ma
from .cor_cycles_placettes import CorCyclePlacetteStagingSchema

class CycleStagingSchema(ma.SQLAlchemyAutoSchema) :

    class Meta :
        model = TCyclesStaging
        include_fk = True
    corCyclesPlacettes= ma.Nested(CorCyclePlacetteStagingSchema, many = True)