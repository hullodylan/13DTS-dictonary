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
    #Category nav/sidebar
    con = create_connection(database)
    query = "SELECT category FROM wordbank"
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    category_ids = cur.fetchall()  # puts the results into a list usable in python
    con.close()
    return render_template('home.html', category=category_ids)



#category link route
@app.route('/category')
def render_category_page():
    con = create_connection(database)

    query = "SELECT maori, english, category, definition, level FROM wordbank"

    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    word_ids = cur.fetchall()  # puts the results into a list usable in python
    con.close()
    return render_template('category.html', wordbank=word_ids)


#Login link route
@app.route('/login')
def render_login_page():
    return render_template('login.html')

#Signup link route
@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    print(request.form)
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    con = create_connection(database)
    query = "INSERT INTO user(id, fname, lname, email, password) VALUES(NULL,?,?,?,?)"

    cur = con.cursor()
    cur.execute(query, (fname, lname, email, password))
    con.commit()
    con.close()


    return render_template('signup.html')


app.run(host='0.0.0.0', debug=True)
