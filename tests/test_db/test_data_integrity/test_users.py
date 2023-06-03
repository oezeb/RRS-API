"""
Test users data integrity
========================

User Roles
----------
The user roles table contains constant values that are set at
the initialization of the database. Therefore, it is forbidden
to insert, delete or update user roles.
"""
from mysql.connector import Error

from app import db

def test_user_roles(app):
    with app.app_context():
        # forbidden to insert user roles
        try:
            db.insert(db.UserRole.TABLE, {'role': -1, 'label': 'test'})
            print("Insert user role forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to delete user roles
        try:
            db.delete(db.UserRole.TABLE)
            print("Delete user role forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to update user roles role
        try:
            db.update(db.UserRole.TABLE, data={'role': -1}, role=db.UserRole.ADMIN)
            print("Update user role role forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
