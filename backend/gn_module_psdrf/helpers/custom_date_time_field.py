from marshmallow import fields, ValidationError
from datetime import datetime

class CustomDateTimeField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValidationError("Invalid datetime format")