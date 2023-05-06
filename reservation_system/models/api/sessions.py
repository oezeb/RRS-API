from marshmallow import Schema

from reservation_system.models.db.session import Session

class SessionGetRespSchema(Schema):
    session_id = Session.session_id()
    name = Session.name()
    start_time = Session.start_time()
    end_time = Session.end_time()

class SessionGetQuerySchema(SessionGetRespSchema):
    pass