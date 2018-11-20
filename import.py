import csv
from application import db


def main():
	with open('books.csv') as csvfile:
		csvreader = csv.DictReader(csvfile, delimiter=',')
		for row in csvreader:
			if db.execute("SELECT isbn FROM books WHERE isbn = :isbn", {'isbn': row['isbn']}).rowcount == 0:
				db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
						   {'isbn': row['isbn'], 'title': row['title'], 'author': row['author'], 'year': row['year']})
		db.commit()


if __name__ == '__main__':
	main()