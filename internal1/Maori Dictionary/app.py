from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

database = "identifier.sqlite"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "secret"


# Creating connection to table
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


# User is logged in or not logged in
def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


# Displays categories on the sidebar
def categories():
    # Category nav/sidebar
    query = "SELECT id, cat_name FROM category"
    con = create_connection(database)
    cur = con.cursor()
    cur.execute(query)
    cat_names = cur.fetchall()
    con.close()
    return cat_names


# User is a teacher or student
def role():
    if session.get('userid') is None:
        print("not logged in")
        role = "None"
        return role
    con = create_connection(database)
    cur = con.cursor()
    userid = session['userid']
    query = "SELECT role FROM user WHERE id = ?"
    cur.execute(query, (userid,))
    admin = cur.fetchall()
    if admin[0][0] == 'teacher':
        print('teacher')
        role = 'teacher'
    elif admin[0][0] == 'student':
        print('student')
        role = 'student'
    else:
        print("neither")
        role = None
    return role


# Homepage route
@app.route('/', methods=['GET', 'POST'])
def render_homepage():
    """
    Route for the homepage

    returns home.html with adding category
    """
    if request.method == 'POST':
        cat_name = request.form.get('cat_name').strip().lower()
        con = create_connection(database)

        query = "INSERT INTO category (cat_name) VALUES(?)"
        cur = con.cursor()

        try:
            cur.execute(query, (cat_name,))
        except sqlite3.IntegrityError:
            return redirect('/?error=category+is+already+used')  # error prevention
        con.commit()
        con.close()
    # error prevention
    error = request.args.get('error')
    if error is None:
        error = ""

    return render_template('home.html', categories=categories(), logged_in=is_logged_in(), error=error, role=role())


# Category route
@app.route('/category/<cat_id>', methods=['GET', 'POST'])
def render_category_page(cat_id):
    """
    Route for each individual category

    Allows user to add a word into the dictionary under the cat_id the page is on

    Returns category.html as the category id
    """
    con = create_connection(database)
    query = "SELECT id, cat_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()

    # Displaying each word on their category
    query = "SELECT cat_id, maori, english, image, id FROM wordbank"
    cur = con.cursor()
    cur.execute(query)
    words = cur.fetchall()

    # User can add word
    if request.method == 'POST':
        maori = request.form.get('maori').strip().lower()
        english = request.form.get('english').strip().lower()
        definition = request.form.get('definition').strip().lower()
        level = request.form.get('level')
        editor_id = session['userid']
        timestamp = datetime.now()
        format_timestamp = timestamp.strftime("%Y-%m-%d %X")
        image_name = "noimage.png"

        query = """INSERT INTO wordbank(id, maori, english, cat_id, definition, level, editor_id, image, timestamp) 
        VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = con.cursor()

        try:
            cur.execute(query, (maori, english, cat_id, definition, level, editor_id, image_name, format_timestamp))
        except sqlite3.IntegrityError:
            return redirect('/category?error=word+is+already+used')  # error prevention
        con.commit()
        con.close()
        return redirect(request.url)
    # error prevention
    error = request.args.get('error')
    if error is None:
        error = ""

    return render_template('category.html', words=words, logged_in=is_logged_in(), categories=categories(),
                           category_id=int(cat_id), error=error, category=category, role=role())


@app.route('/word/<word_id>', methods=['GET', 'POST'])
def render_word_page(word_id):
    """
    Route for each individual word

    Allows user to edit the words details

    Returns word.html as the word id
    """
    # Grabbing the word details
    con = create_connection(database)
    cur = con.cursor()
    query = "SELECT id, maori, english, definition, level, image, timestamp, editor_id FROM wordbank"
    cur.execute(query)
    word_display = cur.fetchall()

    # Grabbing the editors details
    query = "SELECT id, fname FROM user"
    cur = con.cursor()
    cur.execute(query)
    user_name = cur.fetchall()

    # User edits a word
    if request.method == "POST":
        maori = request.form.get('maori').strip().lower()
        english = request.form.get('english').strip().lower()
        definition = request.form.get('definition').strip().lower()
        level = request.form.get('level')
        editor_id = session['userid']
        timestamp = datetime.now()
        format_timestamp = timestamp.strftime("%Y-%m-%d %X")

        query = "UPDATE wordbank SET maori=?, english=?, definition=?,level=?,timestamp=?, editor_id=? WHERE id=?"
        cur.execute(query, (maori, english, definition, level, format_timestamp, editor_id, word_id))
        con.commit()
        return redirect(request.url)

    con.close()
    return render_template('word.html', logged_in=is_logged_in(), categories=categories(), word_id=int(word_id),
                           word_display=word_display, user_name=user_name, role=role())


@app.route('/edit_category/<cat_id>', methods=['GET', 'POST'])
def render_edit_category_page(cat_id):
    """
    Route for editing category name

    Allows user to edit the category name

    Redirects back to home - put to redirect to their category
    """
    con = create_connection(database)
    query = "SELECT id, cat_name FROM category"
    cur = con.cursor()
    cur.execute(query)
    category = cur.fetchall()

    if request.method == 'POST':
        cat_name = request.form.get('cat_name').strip().lower()
        query = "UPDATE category SET cat_name=? WHERE id=?"
        cur.execute(query, (cat_name, cat_id))
        con.commit()
        return redirect('/')
    con.close()

    # error prevention
    error = request.args.get('error')
    if error is None:
        error = ""

    return render_template('edit_category.html', categories=categories(), cat_id=int(cat_id), role=role(),
                           category=category, logged_in=is_logged_in(), error=error)

@app.route('/delete_word/<word_id>')
def render_delete_word_page(word_id):
    """
    Route for deleting an individual word

    User chooses to delete the word selected

    Returns delete_word.html as the word id
    """
    con = create_connection(database)
    query = "SELECT id, maori FROM wordbank "
    cur = con.cursor()
    cur.execute(query)
    word = cur.fetchall()
    con.close()

    return render_template('delete_word.html', categories=categories(), word_id=int(word_id), word=word, role=role(),
                           logged_in=is_logged_in())


@app.route('/delete_category/<cat_id>')
def render_delete_cat_page(cat_id):
    """
        Route for deleting a category

        User chooses to delete the category selected

        Returns delete_category.html as the category id
        """
    con = create_connection(database)
    query = "SELECT id, cat_name FROM category "
    cur = con.cursor()
    cur.execute(query)
    cat = cur.fetchall()
    return render_template('delete_category.html', categories=categories(), category=cat, cat_id=int(cat_id),
                           role=role(), logged_in=is_logged_in())


@app.route('/confirm_delete_cat/<cat_id>', methods=['GET', 'POST'])
def confirm_delete_cat(cat_id):
    """
    Route for confirming deleting a category

    User confrims to delete the category and the words that match the same category id

    Redirects back to homepage after deleting category

    """
    # Deleting words from the category
    con = create_connection(database)
    query = "DELETE FROM wordbank WHERE cat_id=?"
    cur = con.cursor()
    cur.execute(query, (cat_id,))

    # Deleting the category
    query = "DELETE FROM category WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (cat_id,))
    con.commit()
    con.close()
    return redirect('/')


@app.route('/confirm_delete_word/<word_id>', methods=['GET', 'POST'])
def confirm_delete_word(word_id):
    """
    Route for confirming deleting a word

    User confrims to delete the word

    Redirects back to homepage after deleting the word

    """
    # Deleting words from t
    con = create_connection(database)
    query = "DELETE FROM wordbank WHERE id=?"
    cur = con.cursor()
    cur.execute(query, (word_id,))
    con.commit()
    con.close()
    return redirect('/')


@app.route('/dont_delete')
def dont_delete():
    """
    Route for not deleting word or category

    Redirects user back to homepage if they dont want to delete
    """
    return redirect('/')  # Takes user back to homepage if they dont want to delete


@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    """
    Route for login page

    User enters login details
        - checks if they match details in user
            - if they do then login is successful - session is created
            -if not then error occurs - redirected to login page

    Returns login.html

    """
    # Redirecting user if logged in
    if is_logged_in():
        return redirect('/')
    # User enters login details
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        query = """SELECT id, fname, password, role FROM user WHERE email = ? """
        con = create_connection(database)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()
        # See if user entries match login details
        try:
            userid = user_data[0][0]
            fname = user_data[0][1]
            db_password = user_data[0][2]
            role = user_data[0][3]

        except IndexError:
            return redirect("/login?error=Email+invalid+or+password+incorrect")

        # check to see if password matches to email address

        if not bcrypt.check_password_hash(db_password, password):
            return redirect("/login?error=Email+invalid+or+password+incorrect")
        # Creating sessions
        session['email'] = email
        session['userid'] = userid
        session['fname'] = fname
        session['role'] = role

        print(session)
        return redirect('/')

    # error prevention
    error = request.args.get('error')
    if error is None:
        error = ""

    return render_template('login.html', logged_in=is_logged_in(), categories=categories(), error=error)


@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    """
    Route for signup page

    User enters signup details
        - if they dont meet certain requirements then they are redirected to signup page to try again
        - if signup details are suitable, its inserted into user and the password is hashed and then redirected
          to login.html

    Returns signup.html
x
    """
    # Redirecting user if logged in
    if is_logged_in():
        return redirect('/')
    # User creates an account
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        role = request.form.get('role')

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
        query = "INSERT into user(id, fname, lname, email, password, role) VALUES(NULL, ?,?,?,?,?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, role))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=email+is+already+used')
        con.commit()
        con.close()
        return redirect('/login')

    # error prevention
    error = request.args.get('error')
    if error is None:
        error = ""

    return render_template('signup.html', logged_in=is_logged_in(), error=error, categories=categories())


@app.route('/logout')
def logout():
    """
    Route for signout

    Redirects user back to homepage
    """
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


app.run(host='0.0.0.0', debug=True)
