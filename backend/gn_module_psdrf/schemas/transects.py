from flask_marshmallow import fields
from ..models import TTransects
from geonature.utils.env import ma

class TransectSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TTransects
        include_fk = True