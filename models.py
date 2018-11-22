class Book:
	def __init__(self, isbn, title, author, review_ids):
		self.isbn = isbn
		self.title = title
		self.author = author
		self.review_ids = review_ids

	def __str__(self):
		return self.isbn

	def count_reviews(self):
		return len(self.review_ids)


class Review:
	def __init__(self, book_id, author, text):
		self.book_id = book_id
		self.author = author
		self.text = text
		self.rating = 0

	def __str__(self):
		return self.text