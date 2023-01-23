from flask_marshmallow import fields
from ..models import CorCyclesPlacettes
from geonature.utils.env import ma
from .regenerations import RegenerationSchema
from .transects import TransectSchema


class CorCyclePlacetteSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = CorCyclesPlacettes
        include_fk = True
    regenerations = ma.Nested(RegenerationSchema, many = True)
    transects = ma.Nested(TransectSchema, many = True)