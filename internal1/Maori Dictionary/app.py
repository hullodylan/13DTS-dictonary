from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

database = "C:/Users/Dylan Wu/OneDrive - Wellington College/year 13/13DTS-dictonary/internal1/Maori Dictionary/identifier.sqlite"
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

#Homepage link route
@app.route('/')
def render_homepage():
    return render_template('home.html')



#category link route
@app.route('/category')
def render_category_page():
    con = create_connection(database)

    query = "SELECT maori, english, category, definition, level FROM wordbank"

    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    word_ids = cur.fetchall()  # puts the results into a list usable in python
    print(word_ids)
    con.close()
    return render_template('category.html', wordbank=word_ids)





app.run(host='0.0.0.0', debug=True)
