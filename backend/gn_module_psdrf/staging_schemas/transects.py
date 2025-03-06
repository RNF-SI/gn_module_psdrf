from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TTransectsStaging
from geonature.utils.env import ma
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class TransectStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TTransectsStaging
        include_fk = True

    @post_load
    def make_transect(self, data, **kwargs):
        return TTransectsStaging(**data)