from flask_marshmallow import fields
from ..models import TPlacettes
from geonature.utils.env import ma
from .arbres import ArbreSchema
from .bms_sup_30 import BmSup30Schema
from .reperes import RepereSchema
import shapely
from geoalchemy2.shape import to_shape


class PlacetteSchema(ma.SQLAlchemyAutoSchema) :
    geom = fields.fields.Method('wkt_to_geojson')
    geom_wgs84 = fields.fields.Method('wkt_to_geojson')

    #fonction permettant de serialiser les données géographiques, à voir si on ne peut pas factoriser cette fonction
    def wkt_to_geojson(self, obj):
        if obj.geom :
            return shapely.geometry.mapping(to_shape(obj.geom))
        if obj.geom_wgs84 :
            return shapely.geometry.mapping(to_shape(obj.geom_wgs84))
        else :
            return None

    class Meta :
        model = TPlacettes
        include_fk = True
    arbres = ma.Nested(ArbreSchema, many = True)
    bmsSup30 = ma.Nested(BmSup30Schema, many = True)
    reperes = ma.Nested(RepereSchema, many = True)