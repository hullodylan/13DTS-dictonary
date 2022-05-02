from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

database = "identifier.sqlite"
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

# If user is logged in
def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

# Displays categories on sidebar
def categories():
    # Category nav/sidebar
    query = "SELECT id, cat_name FROM category"
    con = create_connection(database)
    cur = con.cursor()
    cur.execute(query)
    cat_names = cur.fetchall()
    con.close()
    return cat_names




# Homepage link route
@app.route('/', methods=['GET', 'POST'])
def render_homepage():
    if request.method == 'POST':
        cat_name =request.form.get('cat_name').strip().lower()
        con = create_connection(database)

        query = "INSERT INTO category(cat_name) VALUES(?)"
        cur = con.cursor()  # You need this line next

        try:
            cur.execute(query, (cat_name, ))  # this line actually executes the query
        except sqlite3.IntegrityError:
            return redirect('/?error=category+is+already+used')
        con.commit()
        con.close()

    error = request.args.get('error')
    if error == None:
        error = ""

    return render_template('home.html', categories=categories(), logged_in=is_logged_in(), error=error)

# category link route
@app.route('/category/<cat_id>',methods=['GET', 'POST'])
def render_category_page(cat_id):
    con = create_connection(database)

# Displaying each word on their category
    query = "SELECT cat_id, maori, english, image, id FROM wordbank"
    cur = con.cursor()
    cur.execute(query)
    words = cur.fetchall()

    query = "SELECT id, cat_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()

# User can add word
    if request.method == 'POST':
        maori = request.form.get('maori')
        english = request.form.get('english')
        definition = request.form.get('definition')
        level = request.form.get('level')
        editor_id = session['userid']
        timestamp = datetime.now()
        image_name = "noimage.png"


        query = """INSERT INTO wordbank(id, maori, english, cat_id, definition, level, editor_id, image, timestamp) 
        VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = con.cursor()

        try:
            cur.execute(query, (maori, english, cat_id, definition, level, editor_id, image_name, timestamp))
        except sqlite3.IntegrityError:
                return redirect('/category?error=word+is+already+used')
        con.commit()
        con.close()
        return redirect(request.url)

    error = request.args.get('error')
    if error == None:
        error = ""

    return render_template('category.html', words=words, logged_in=is_logged_in(), categories=categories(),
                           category_id=int(cat_id), error=error, category=category)

# Takes user to specific word details page
@app.route('/word/<word_id>', methods=['GET', 'POST'])
def render_word_page(word_id):
    # Grabbing the word details
    query = "SELECT id, maori, english, definition, level, image, timestamp, editor_id FROM wordbank"
    con = create_connection(database)
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    word_display = cur.fetchall()  # puts the results into a list usable in python

# Grabbing the editors details
    query = """SELECT id, fname FROM user"""
    cur = con.cursor()  # You need this line next
    cur.execute(query)  # this line actually executes the query
    user_name = cur.fetchall()  # puts the results into a list usable in python
    con.close()

#Add edit word stuff


    return render_template('word.html', logged_in=is_logged_in(), categories=categories(), word_id=int(word_id),
                           word_display=word_display, user_name=user_name)

# User can delete a word - doesnt work
@app.route('/delete_word/<word_id>')
def render_delete_word_page(word_id):
    con = create_connection()
    query = "DELETE FROM wordbank WHERE id=?"
    cur.execute(query)  # this line actually executes the query
    word_display = cur.fetchall()  # puts the results into a list usable in python

    return render_template('delete_word.html', categories=categories(), word_id=word_id)

# User can delete a category
@app.route('/delete_category')
def render_delete_cat_page():
    return render_template('delete_category.html', categories=categories())



# Login link route
@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in():
        return redirect('/')

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        query = """SELECT id, fname, password FROM user WHERE email = ? """
        con = create_connection(database)
        cur = con.cursor()  # You need this line next
        cur.execute(query, (email,))  # this line actually executes the query
        user_data = cur.fetchall()
        con.close()

        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

# check if the password is incorrect for that email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+invalid+or+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        print(session)
        return redirect('/')

    return render_template('login.html', logged_in=is_logged_in(), categories=categories())


# Signup link route
@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():
        return redirect('/')

    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

# user error prevention
        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')
        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')
        if len(fname) < 2:
            return redirect('/signup?error=First+name+must+be+2+characters+or+more')
        if len(lname) < 1:
            return redirect('/signup?error=Last+name+must+be+2+characters+or+more')
        if len(email) < 6:
            return redirect('/signup?error=please+enter+a+valid+email')

        hashed_password = bcrypt.generate_password_hash(password)

        con = create_connection(database)
        query = "INSERT into user(id, fname, lname, email, password) VALUES(NULL, ?,?,?,?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+used')
        con.commit()
        con.close()

        return redirect('/login')
# Error prevention
    error = request.args.get('error')
    if error == None:
        error = ""

    return render_template('signup.html', logged_in=is_logged_in(), error=error, categories=categories())

# Allowing the user to log out
@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')



app.run(host='0.0.0.0', debug=True)
