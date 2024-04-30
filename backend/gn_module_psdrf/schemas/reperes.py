from flask_marshmallow import fields
from ..models import TReperes
from geonature.utils.env import ma

class RepereSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TReperes
        include_fk = True