from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TBmSup30MesuresStaging
from geonature.utils.env import ma
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class BmSup30MesureStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TBmSup30MesuresStaging
        include_fk = True

    @post_load
    def make_bm_sup_30_mesure(self, data, **kwargs):
        return TBmSup30MesuresStaging(**data)