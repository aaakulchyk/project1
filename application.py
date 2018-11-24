import os, hashlib

from flask import Flask, session, render_template, request, redirect, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Book


app = Flask(__name__)

# Check for environment variable
os.putenv('DATABASE_URL', 'postgres://lfmoyqcmuvfoqn:c57be9c5cdd24c0fbe274db8c6626346f1ed8c47b3d8ec0317f73eae8d258337@ec2-50-19-249-121.compute-1.amazonaws.com:5432/d83lec9qlit9jv')
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Define globals for passwords
SALT = 'CS50W_project1'
PER_PAGE = 10

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
            session.pop('username', None)
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
                session['username'] = user_data[1]
                return redirect(url_for('index'))

            # Else raise error
            else:
                return render_template('error.html', message='Password doesn\'t match')

@app.route('/search/', defaults={'page': 1})
@app.route('/search/page/<int:page>')
def search(page, methods=['GET', 'POST']):
    query = request.args.get('search')
    query = '%' + query + '%'

    result = [item for item in db.execute("SELECT isbn, title, author FROM books WHERE isbn LIKE :q "
                                          "OR title LIKE :q "
                                          "OR author LIKE :q",
                                          {'q': query})]
    if not result and page != 1:
        abort(404)
    return render_template('search.html', result=result)

@app.route('/books/<int:id>', methods=['GET', 'POST'])
def book(id):
    if request.method == 'GET':
        # Fetch book with a given id.
        result = db.execute("SELECT id, isbn, title, author, year FROM books WHERE id = :id", {'id': id})
        # Create a dict containing book information.
        for row in result:
            book_data = dict(row)
        if book_data:
            # Collect reviews related to the book.
            reviews_data = db.execute("SELECT book_id, author_id, rating, text, users.username FROM reviews JOIN users ON users.id = author_id WHERE book_id = :id",
                                                {'id': id})
            reviews_list = [dict(review) for review in reviews_data]
            for review in reviews_data:
                review = dict(review)
            print(reviews_list)
            return render_template('book.html', book=book_data, reviews=reviews_list)
        else:
            return render_template('error.html', message='Sorry! We can\'t find this book in our library :(')
    # Submitting a form.
    elif request.method == 'POST':
        # Check whether review is not empty.
        review_text = request.form.get('review-text')
        if review_text is not None:
            # Add review.
            db.execute("INSERT INTO reviews (book_id, author_id, rating, text) VALUES (:book_id, :author_id, :rating, :text)",
                       {'book_id': id, 'author_id': session['user_id'], 'rating': request.form.get('review-rating'), 'text': review_text})
            db.commit()
            # Redirect to the same page.
            return redirect('/books/' + str(id))
        else:
            return render_template('error.html', message='Sorry! We can\'t add an empty review.')