import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    __tablename__= "books"
    id = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.Varchar, nullable=False)
    title = db.Column(db.Varchar, nullable=False)
    author = db.Column(db.Varchar, nullable=False)
    reviews = db.relationship("Reviews", backref="book", lazy=True)

    def add_review(self, review):
        r = Review(review=review, id_books=self.id)
        db.session.add(r)
        db.session.commit()

class Review(db.Model):
    __tablename__ = "reviews"
    reviews = db.Column(db.Varchar, nullable=False)
    id_books = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)