from flask_marshmallow import fields
from ..pr_psdrf_staging_functions.models_staging import TPlacettesStaging
from geonature.utils.env import ma
from .arbres import ArbreStagingSchema
from .bms_sup_30 import BmSup30StagingSchema
from .reperes import RepereStagingSchema
import shapely
from geoalchemy2.shape import to_shape


class PlacetteStagingSchema(ma.SQLAlchemyAutoSchema) :
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
        model = TPlacettesStaging
        include_fk = True
    arbres = ma.Nested(ArbreStagingSchema, many = True)
    bmsSup30 = ma.Nested(BmSup30StagingSchema, many = True)
    reperes = ma.Nested(RepereStagingSchema, many = True)