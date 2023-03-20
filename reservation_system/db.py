import mysql.connector

import click
from flask import current_app, g

# ----------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------
def get_cnx():
    if 'cnx' not in g:
        g.cnx = mysql.connector.connect(
            database=current_app.config['DATABASE'],
            user    =current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD']
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

def select(table, where: dict=None):
    cursor = get_cursor()
    if where is not None and where != {}:
        print("HERE", where)
        cursor.execute(f"""
            SELECT * FROM {table} WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else:
        cursor.execute(f"SELECT * FROM {table};")
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def delete(table, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    if where is not None and where != {}:
        cursor.execute(f"""
            DELETE FROM {table} WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else:
        cursor.execute(f"DELETE FROM {table};")
    cnx.commit(); cursor.close()

def insert(table, data_list):
    cnx = get_cnx(); cursor = cnx.cursor()
    auto_increments = []
    for data in data_list:
        cursor.execute(f"""
            INSERT INTO {table} ({', '.join(data.keys())}) VALUES ({', '.join(['%s']*len(data))});
        """, (*data.values(),))
        auto_increments.append(cursor.lastrowid)
    cnx.commit(); cursor.close()
    return {'auto_increments': auto_increments}