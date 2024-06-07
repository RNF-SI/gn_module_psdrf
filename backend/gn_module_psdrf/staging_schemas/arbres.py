from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TArbresStaging
from geonature.utils.env import ma
from .arbres_mesures import ArbreMesureStagingSchema
from ..helpers.custom_date_time_field import CustomDateTimeField
from marshmallow import post_load

class ArbreStagingSchema(ma.SQLAlchemyAutoSchema) :
    updated_at = CustomDateTimeField(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta :
        model = TArbresStaging
        include_fk = True
    arbres_mesures = ma.Nested(ArbreMesureStagingSchema, many = True)

    @post_load
    def make_arbre(self, data, **kwargs):
        return TArbresStaging(**data)