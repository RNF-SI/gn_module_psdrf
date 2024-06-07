from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TBmSup30Staging
from geonature.utils.env import ma
from .bms_sup_30_mesures import BmSup30MesureStagingSchema
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class BmSup30StagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TBmSup30Staging
        include_fk = True
    bm_sup_30_mesures = ma.Nested(BmSup30MesureStagingSchema, many = True)

    @post_load
    def make_bm_sup_30(self, data, **kwargs):
        return TBmSup30Staging(**data)