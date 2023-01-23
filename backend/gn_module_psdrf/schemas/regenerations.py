from flask_marshmallow import fields
from ..models import TRegenerations
from geonature.utils.env import ma

class RegenerationSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TRegenerations
        include_fk = True