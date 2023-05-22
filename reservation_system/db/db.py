import logging
import typing
from datetime import datetime

import click
import mysql.connector
from flask import current_app, g

from .schema import init_schema

logger = logging.getLogger(__name__)

def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)

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

# ----------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_db():
    cnx = get_cnx(); cursor = cnx.cursor()

    set_current_time_zone(cursor)
    init_schema(cursor)
    
    cnx.commit(); cursor.close()

def set_current_time_zone(cursor):
    offset = datetime.now() - datetime.utcnow()
    hours = offset.total_seconds() // 3600
    minutes = (offset.total_seconds() % 3600) // 60
    sign = '+' if hours >= 0 else '-'
    offset = "%s%02d:%02d" % (sign, abs(hours), minutes)
    cursor.execute(f"SET @@GLOBAL.time_zone = '{offset}';")
    cursor.execute(f"SET @@SESSION.time_zone = '{offset}';")

# ----------------------------------------------------------------
# Database CRUD operations
# ----------------------------------------------------------------

def execute(query, values):
    """Execute a query and return produced data and cursor."""
    cnx = get_cnx(); cursor = cnx.cursor(dictionary=True)
    cursor.execute(query, values)
    data = cursor.fetchall()
    cnx.commit(); cursor.close()
    return data, cursor

def insert(table, data: typing.Mapping[str, typing.Any]):
    """Insert a row into the table."""
    cols = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({cols}) VALUES ({values})"

    # execute query
    _, cursor = execute(query, tuple(data.values()))

    lastrowid, rowcount = cursor.lastrowid, cursor.rowcount
    return {"lastrowid": lastrowid, "rowcount": rowcount}

def select(
        table,
        columns: typing.Iterable[str]=None, 
        order_by: typing.Iterable[str]=None, 
        order: str="ASC",
        **where,
    ):
    """Select rows from the table.

    parameters:
        - `table`: table name
        - `columns`: a list of column names to be selected
        - `order_by`: a list of column names to be ordered by
        - `order`: 'ASC' or 'DESC'
    """
    values = {}
    # columns
    if columns is None or len(columns) == 0:
        columns = '*'
    else:
        columns = ', '.join(columns)

    # order by clause
    if order_by is None or len(order_by) == 0:
        order_by = ""
    else:
        order_by = f" ORDER BY {', '.join(order_by)} {order}"

    # where clause
    if where is None or len(where) == 0:
        where = ""
    else:
        values = where.values()
        where = f" WHERE {' AND '.join([f'{k}=%s' for k in where])}"
    
    query = f"SELECT {columns} FROM {table}{where}{order_by}"

    # execute query
    data, _ = execute(query, tuple(values))
    return data

def update(
        table,
        data: typing.Mapping[str, typing.Any],
        **where,
    ):
    """Update rows in the table.

    parameters:
        - `table`: table name
        - `data`: a dictionary of column-value pairs to be updated
    """
    # data
    values = list(data.values())
    data = ', '.join([f'{k}=%s' for k in data])

    # where clause
    if where is None or len(where) == 0:
        where = ""
    else:
        values += list(where.values())
        where = f" WHERE {' AND '.join([f'{k}=%s' for k in where])}"
    
    query = f"UPDATE {table} SET {data}{where}"

    # execute query
    _, cursor = execute(query, tuple(values))

    return {"rowcount": cursor.rowcount}

def delete(table, **where):
    """Delete rows from the table."""
    values = list(where.values())
    where = ' AND '.join([f'{k}=%s' for k in where])
    query = f"DELETE FROM {table} WHERE {where}"

    # execute query
    _, cursor = execute(query, tuple(values))

    return {"rowcount": cursor.rowcount}
