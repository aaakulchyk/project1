import csv
from application import db


with open('books.csv') as csvfile:
	csvreader = csv.reader(csvfile, delimiter=',')
	for row in csvreader:
		if db.execute("SELECT isbn FROM books WHERE isbn = :isbn", {'isbn': row[0]}).rowcount == 0:
			db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
					   {'isbn': row[0], 'title': row[1], 'author': row[2], 'year': row[3]})
	db.commit()