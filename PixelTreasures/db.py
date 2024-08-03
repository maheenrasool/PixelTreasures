import click 
import mysql.connector
import os
from flask import current_app, g
from flask.cli import with_appcontext 



def get_db():

    #connect database

    if 'db' not in g or not g.db.is_connected():
        g.db = mysql.connector.connect(
            host  = current_app.config["DB_HOST"],
            user = current_app.config["DB_USER"],
            password = current_app.config["DB_PASSWORD"],
            db = current_app.config["DB_DATABASE"]

        )
    return g.db

def close_db( e=None):

    #close the database

    db = g.pop('db', None)

    if db is not None and db.is_connected():
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)