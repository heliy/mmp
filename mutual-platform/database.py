#coding:UTF-8

from sqlite3 import dbapi2 as sqlite
from flask import _app_ctx_stack

def get_db():
    """
    Opend a new database connection if there is none yet for the
    current application context.
    """    
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite.connect(app.config["DATABASE"])
        top.sqlite_db.row_factory = sqlite.Row
    return top.sqlite_db

@app.teardown_appcontext
def close_db(exception):
    """
    Close the database again at the end of the request.
    """
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().execetescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """ Creates the database tables. """
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """ Queries the database and returns a list of dictionaries. """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv
