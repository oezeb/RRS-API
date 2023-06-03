from marshmallow import Schema as _Schema
from marshmallow import fields

from .notices import *
from .periods import *
from .reservations import *
from .rooms import *
from .sessions import *
from .settings import *
from .users import *

from .auth import *


class Schema(_Schema):
    required_fields = ()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, 'required_fields'):
            for field in self.required_fields:
                if field in self.fields:
                    self.fields[field].required = True

class Label(Schema):
    label = fields.Str()
    description = fields.Str()

class Many:
    """Order is important. Extend this class first, then extend Schema."""
    def __init__(self, many=None, **kwargs):
        super().__init__(many=True, **kwargs)
