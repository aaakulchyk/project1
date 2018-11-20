import os, hashlib

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
DATABASE_URL = 'postgres://lfmoyqcmuvfoqn:c57be9c5cdd24c0fbe274db8c6626346f1ed8c47b3d8ec0317f73eae8d258337@ec2-50-19-249-121.compute-1.amazonaws.com:5432/d83lec9qlit9jv'
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Define salt for passwords
SALT = 'CS50W_project1'

@app.route("/")
def index():
    return render_template('home.html')


@app.route('/registration', methods=['GET', 'POST'])
def register():
    # Just show registration form
    if request.method == 'GET':
        return render_template('registration.html')

    # When the form is submitted
    elif request.method == 'POST':
        global SALT
        username = request.form.get('username')
        password = hashlib.sha256(SALT.encode() + request.form.get('password').encode()).hexdigest()
        if db.execute("SELECT username FROM users WHERE username = :username",
                      {'username': username}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                       {'username': username,
                        'password': password})
            db.commit()
            return redirect(url_for('index'))
        else:
            return render_template('error.html', message='A user with this username already exists.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global SALT

    # When user submits the form, query the db
    if request.method == 'POST':

        # If user is authorized, log out
        if session.get('user_id') is not None:
            session.pop('user_id', None)
            return redirect(url_for('index'))

        # Otherwise, log in
        else:
            username = request.form.get('username')
            password = hashlib.sha256(SALT.encode() + request.form.get('password').encode()).hexdigest()
            user_data = db.execute("SELECT * FROM users WHERE username = :username",
                                   {'username': username}).fetchone()

            # If password is correct, continue
            if password == user_data[-1]:
                session['user_id'] = user_data[0]
                return redirect(url_for('index'))

            # Else raise error
            else:
                return render_template('error.html', message='Password doesn\'t match')
