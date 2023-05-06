import base64

from marshmallow import fields

class TimeDeltaField(fields.TimeDelta):
    def _serialize(self, value, attr, obj, **kwargs):
        seconds = super()._serialize(value, attr, obj, **kwargs)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return "%02d:%02d:%02d" % (h, m, s)
    
class ImageField(fields.Str):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return base64.b64encode(value).decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return base64.b64decode(value)