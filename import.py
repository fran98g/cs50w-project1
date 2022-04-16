import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://bmyzzbdtsdtgmz:433e03dc9b43e82b78752708b8fbb7a0f85182de1414d0905589b799ac430767@ec2-18-215-96-22.compute-1.amazonaws.com:5432/ddr59gn3kq765q")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for ISBN, title, author, year in reader:
        db.execute("INSERT INTO books (ISBN, title, author, year) VALUES (:ISBN, :title, :author, :year)", {"ISBN": ISBN, "title": title, "author": author, "year": year})
        db.commit()
        print(f"Se acaba de agregar el libro con codigo {ISBN} de titulo {title} del autor {author} del año {year}.")

if __name__ == "__main__":
    main()