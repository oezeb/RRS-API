import logging
from datetime import datetime, timedelta
import os

from flask.testing import FlaskClient

from reservation_system import db

logger = logging.getLogger(__name__)

def test_data(client: FlaskClient, app):
    with app.app_context():
        # add notices
        logger.info("Adding notices...")
        res = db.insert(db.Notice.TABLE, [{
                "username": "admin",
                "title": "系统维护",
                "content": "系统将于2020年1月1日0时至2020年1月1日1时进行维护，期间将无法使用。",
            },
            {
                "username": "admin",
                "title": "简单通知公告",
                "content": "测试图片是否能够正常显示。\n\n![图片](http://127.0.0.1:5000/static/attachments/1.jpg)\n",
            }]
        )
        
        assert len(res['last_ids']) == 2
        id = res['last_ids'][0]
        res = db.update(db.Notice.TABLE, { 'username': 'advanced' }, where={ 'notice_id': id })
        assert res == 1


        # insert image into `rooms` table as BLOB where room_id = 1
        filename = os.path.join(os.path.dirname(__file__), '1.jpg')
        with open(filename, 'rb') as f:
            data = f.read()
            logger.info("Update room_id=1's image...")
            res = db.update(db.Room.TABLE, { 'image': data }, where={ 'room_id': 1 })
            assert res == 1