from flask_marshmallow import fields
from ..models import TBmSup30Mesures
from geonature.utils.env import ma

class BmSup30MesureSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TBmSup30Mesures
        include_fk = True