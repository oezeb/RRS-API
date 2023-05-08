from reservation_system.models import db
from reservation_system.models import api
from reservation_system.models import auth
from reservation_system.models import user_api
from reservation_system.models import util

from marshmallow import Schema

import logging

logger = logging.getLogger(__name__)

# def register_components(spec):
#     for mod in [api, auth, user_api]:
#         for name, value in mod.__dict__.items():
#             if isinstance(value, type) and issubclass(value, Schema):
#                 if name not in spec.components.schemas:
#                     spec.components.schema(name, schema=value)
#                 else:
#                     logger.warning(f'Schema {name} already registered')

__all__ = ['db', 'api', 'auth', 'user_api', 'util']