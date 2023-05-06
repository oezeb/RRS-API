from marshmallow import Schema

from reservation_system.models.db.notice import Notice

class NoticeGetRespSchema(Schema):
    notice_id = Notice.notice_id()
    username = Notice.username()
    title = Notice.title()
    content = Notice.content()
    create_time = Notice.create_time()
    update_time = Notice.update_time()

class NoticeGetQuerySchema(NoticeGetRespSchema):
    pass