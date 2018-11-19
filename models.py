import hashlib
from .application import db

class User:
    counter = 1
    def __init__(self, username, password):
        self.username = username
        self.password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
        User.counter += 1

    def __str__(self):
        return self.username

    def rename(self, name):
        self.username = name

	def change_password(self, password, new_password):
		if password == db.execute("SELECT password FROM users WHERE password = :password",
								  {'password': password,}).first and password != new_password:
			self.password = new_password


class Book:
	def __init__(self, author, title, isbn, **info):
		self.author = author
		self.title = title
		self.isbn = isbn
		if info['description']:
			self.description = info['description']


class Review:
	counter = 1
	def __init__(self, author_id, book_id, text):
		self.author_id = author_id
		self.book_id = book_id
		self.text = text
		self.status = 'published'
		Review.counter += 1

	def __str__(self):
		return self.text

	def redact(self, new_text):
		if self.text != new_text:
			self.text = new_text
			self.status = 'redacted'