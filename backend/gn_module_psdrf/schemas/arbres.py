from flask_marshmallow import fields
from ..models import TArbres
from geonature.utils.env import ma
from .arbres_mesures import ArbreMesureSchema

class ArbreSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TArbres
        include_fk = True
    arbres_mesures = ma.Nested(ArbreMesureSchema, many = True)

