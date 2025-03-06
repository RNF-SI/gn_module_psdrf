from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TRegenerationsStaging
from geonature.utils.env import ma
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class RegenerationStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TRegenerationsStaging
        include_fk = True

    @post_load
    def make_regeneration(self, data, **kwargs):
        return TRegenerationsStaging(**data)