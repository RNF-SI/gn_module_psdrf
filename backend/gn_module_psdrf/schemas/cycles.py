from flask_marshmallow import fields
from ..models import TCycles
from geonature.utils.env import ma
from .cor_cycles_placettes import CorCyclePlacetteSchema


class CycleSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TCycles
        include_fk = True
    corCyclesPlacettes= ma.Nested(CorCyclePlacetteSchema, many = True)

class ConciseCycleSchema(ma.SQLAlchemyAutoSchema) :
    class Meta :
        model = TCycles
        include_fk = True
