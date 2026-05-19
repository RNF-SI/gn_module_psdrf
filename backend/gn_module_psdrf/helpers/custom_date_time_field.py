from marshmallow import fields, ValidationError
from datetime import datetime

class CustomDateTimeField(fields.Field):
    def __init__(self, *args, format=None, **kwargs):
        # `format` is accepted for backwards-compat with older marshmallow usage;
        # the deserialization format is hardcoded below.
        super().__init__(*args, **kwargs)
        self._format = format

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValidationError("Invalid datetime format")