from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TReperesStaging
from geonature.utils.env import ma
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class RepereStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TReperesStaging
        include_fk = True

    @post_load
    def make_repere(self, data, **kwargs):
        return TReperesStaging(**data)