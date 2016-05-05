#coding:UTF-8

import os

from sqlite3 import dbapi2 as sqlite
from flask import _app_ctx_stack

from config import *
from mmp import app

def get_db():
    """
    Opend a new database connection if there is none yet for the
    current application context.
    """    
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite.connect(DATABASE)
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

# def init_db():
#     db = get_db()
#     with app.open_resource('schema.sql', mode='r') as f:
#         db.cursor().execetescript(f.read())
#     db.commit()


def query_db(query, args=(), one=False):
    """ Queries the database and returns a list of dictionaries. """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def test_init():
    need_init = False
    if DATABASE not in os.listdir('.'):
        need_init = True
    db = sqlite.connect(DATABASE)
    db.row_factory = sqlite.Row

    if need_init:
        with open('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
    return db

# database = test_init()

# def test_get(db=database):
#     return db

# def test_query(query, args=(), one=False):
#     cur = test_get().execute(query, args)
#     rv = cur.fetchall()
#     return (rv[0] if rv else None) if one else rv

# def test_close(db=database):
#     db.close()  

