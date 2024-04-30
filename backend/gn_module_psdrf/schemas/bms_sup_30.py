from flask_marshmallow import fields
from ..models import TBmSup30
from geonature.utils.env import ma
from .bms_sup_30_mesures import BmSup30MesureSchema

class BmSup30Schema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TBmSup30
        include_fk = True
    bm_sup_30_mesures = ma.Nested(BmSup30MesureSchema, many = True)
