from flask_marshmallow import fields
from ..models import TArbresMesures
from geonature.utils.env import ma

class ArbreMesureSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TArbresMesures
        include_fk = True