from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

#C:/Users/18004/OneDrive - Wellington College/year 13/internal1/Maroi Dictionary
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "secret"

def create_connection(db_file):
    """create a connection to the sqlite db"""
    try:
        connection = sqlite3.connect(db_file)
        connection.execute('pragma foreign_keys=ON')
        # initialise_tables(connection)
        return connection
    except Error as e:
        print(e)
    return None

@app.route('/')
def render_homepage():
        return render_template('home.html')

