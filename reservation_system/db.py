import mysql.connector

import click
from flask import current_app, g

def get_cnx():
    if 'cnx' not in g:
        g.cnx = mysql.connector.connect(
            database=current_app.config['DATABASE'],
            user='test',
            password='password'
        )
        
    return g.cnx


def close_cnx(e=None):
    cnx = g.pop('cnx', None)

    if cnx is not None:
        cnx.close()

def get_cursor():
    cnx = get_cnx()
    return cnx.cursor()


def init_db():
    cnx = get_cnx()
    cursor = cnx.cursor()

    with current_app.open_resource('schema.sql') as f:
        for statement in f.read().decode('utf8').split(';'):
            if statement.strip() != "":
                cursor.execute(statement)
    cnx.commit()
    cursor.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)

# Users
USERS_TABLE = "users"
def insert_users(users):
    cnx = get_cnx(); cursor = cnx.cursor()
    for user in users:
        cursor.execute(f"""
            INSERT INTO {USERS_TABLE} ({', '.join(user.keys())}) VALUES ({', '.join(['%s']*len(user))});
        """, (*user.values(),))
    cnx.commit(); cursor.close()

def get_user(username):
    cursor = get_cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s;', (username,))
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))

# def get_users(where: dict=None):
#     cursor = get_cursor()
#     if where is not None:
#         cursor.execute(f"""
#             SELECT * FROM {USERS_TABLE} WHERE {' AND '.join([f'{name} = %s' for name in where])};
#         """, (*where.values(),))
#     else:
#         cursor.execute(f"SELECT * FROM {USERS_TABLE};")
#     columns = [col[0] for col in cursor.description]
#     return [dict(zip(columns, row)) for row in cursor.fetchall()]
