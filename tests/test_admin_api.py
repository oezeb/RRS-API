import json
import os

from data import *
from test_auth import auth_client

from app import db

BASE_URL = "http://127.0.0.1:5000/api/admin"

def test_get_reservations(client, app):
    pass

def test_post_reservation(client, app):
    pass

def test_patch_reservation(client, app):
    pass


def test_get_reservation_status(client, app):
    pass

def test_patch_reservation_status(client, app):
    pass


def test_get_reservation_privacy(client, app):
    pass

def test_patch_reservation_privacy(client, app):
    pass


def test_get_users(client, app):
    pass

def test_post_user(client, app):
    pass

def test_patch_user(client, app):
    pass


def test_get_user_roles(client, app):
    pass

def test_patch_user_roles(client, app):
    pass


def test_get_rooms(client, app):
    pass

def test_post_room(client, app):
    pass

def test_patch_room(client, app):
    pass

def test_delete_room(client, app):
    pass


def test_get_room_types(client, app):
    pass

def test_post_room_type(client, app):
    pass

def test_patch_room_type(client, app):
    pass

def test_delete_room_type(client, app):
    pass


def test_get_room_status(client, app):
    pass

def test_patch_room_status(client, app):
    pass


def test_get_languages(client, app):
    pass

def test_patch_language(client, app):
    pass


def test_get_sessions(client, app):
    pass

def test_post_session(client, app):
    pass

def test_patch_session(client, app):
    pass

def test_delete_session(client, app):
    pass


def test_get_notices(client, app):
    pass

def test_post_notice(client, app):
    pass

def test_patch_notice(client, app):
    pass

def test_delete_notice(client, app):
    pass


def test_get_periods(client, app):
    pass

def test_post_period(client, app):
    with app.app_context():
        insert_data(only=['users'])
        users = {user['username']: user for user in get_users()}
        
        # Get admin username
        res = db.select(db.User.TABLE, role=db.UserRole.ADMIN)
        assert len(res) > 0
        username = res[0]['username']
        password = users[username]['password']

        # Login as admin
        auth_client(client, username, password)

        res = client.post(
            f'{BASE_URL}/periods', 
            json={
                'start_time': '22:00',
                'end_time': '23:00',
            }
        )
        assert res.status_code == 201
        assert res.json['period_id'] is not None

def test_patch_period(client, app):
    pass

def test_delete_period(client, app):
    pass


def test_get_settings(client, app):
    pass

def test_patch_setting(client, app):
    pass
