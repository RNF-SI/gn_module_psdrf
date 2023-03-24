from flask_marshmallow import fields
from ..models import BibEssences
from geonature.utils.env import ma

class EssenceSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = BibEssences
        include_fk = False