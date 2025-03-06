from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import CorCyclesPlacettesStaging
from geonature.utils.env import ma
from .regenerations import RegenerationStagingSchema
from .transects import TransectStagingSchema
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class CorCyclePlacetteStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)


    class Meta :
        model = CorCyclesPlacettesStaging
        include_fk = True
    regenerations = ma.Nested(RegenerationStagingSchema, many = True)
    transects = ma.Nested(TransectStagingSchema, many = True)

    @post_load
    def make_cor_cycle_placette(self, data, **kwargs):
        return CorCyclesPlacettesStaging(**data)