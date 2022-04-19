import os

from flask import Flask, render_template, request, session, redirect, jsonify
# from crypt import methods
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import FetchedValue, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import *
import json
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://bmyzzbdtsdtgmz:433e03dc9b43e82b78752708b8fbb7a0f85182de1414d0905589b799ac430767@ec2-18-215-96-22.compute-1.amazonaws.com:5432/ddr59gn3kq765q")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
#@login_required
def index():
    books = db.execute("SELECT * FROM books").fetchall()
    db.commit()
    return render_template("index.html", books=books)

@app.route("/books", methods=["GET"])
@login_required
def books():
    """Search a book"""

    # Get form information.
    name = request.args.get("q")
    if not name:
        return render_template("error.html", message="No se posee registro de ese libro.")
    name = "%" + name + "%"

    rows = db.execute("SELECT * FROM books WHERE isbn LIKE :name OR title LIKE :name OR author LIKE :name", {"name":name}).fetchall()

    return render_template("books.html", books=rows)
# prueba


@app.route("/book", methods=["GET"])
def book():
    """List details about a single book."""

    isbn = request.args.get("isbn")
    if isbn == None:
        return render_template("error.html", message="No se posee registro de ese libro.")
    #isbn = "%" + isbn + "%"

    rows2 = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn":isbn}).fetchone()
    libroo = rows2[0]
    review = request.args.get("review")
    rows3 = db.execute("SELECT * FROM review WHERE id_books =:libroo", {"libroo":libroo}).fetchall()
    return render_template("book.html", book=rows2, review=rows3)


@app.route("/review", methods=["POST"])
def reviews():
    """Make a review"""
    star = request.form.get("star")
    review = request.form.get("review")
    libro = request.form.get("libro")
    print(libro)
    libro_obj=db.execute("SELECT * FROM books WHERE isbn =:libro", {"libro":libro}).fetchone()
    id_books = libro_obj["id_books"]
    id_user = session["user_id"]
    print(id_user+1)
    username = db.execute("SELECT username FROM users WHERE id_username =:id_username", {"id_username":id_user}).fetchone()
    rows4 = db.execute("INSERT INTO review (id_user, id_books, review, star, username) VALUES (:id_user, :id_books, :review, :star, :username)", {
        "id_user":f"{id_user}",
        "id_books":id_books,
        "review":review,
        "star":star,
        "username":username[0],
    })
    db.commit()
    return redirect("/book?isbn="+libro)

@app.route("/api", methods=["GET"])
@login_required
def book_api():
    #url = f'https://www.googleapis.com/books/v1/volumes?q='+isbn
    #r = requests.get(url)
    #data = json.loads(r.text)

    isbn = request.args.get("isbn")    

    api = db.execute("SELECT * FROM books WHERE isbn =:isbn", {"isbn":isbn}).fetchone()
    id_books = api["id_books"]

    if api == None:
        return jsonify({"error": "isbn del libro es invalido"}),422

    reviews = db.execute("SELECT COUNT(review) AS conteo FROM review WHERE id_books =:id_books", {"id_books":id_books}).fetchone()
    score = db.execute("SELECT SUM(star) AS suma FROM review WHERE id_books =:id_books", {"id_books":id_books}).fetchone()
    print(reviews)
    print(score)
    return jsonify({
        "title" : api["title"],
        "author": api["author"],
        "year": api["year"],
        "isbn": api["isbn"],
        "review_count": reviews["conteo"],
        "average_score": score["suma"],
    }),200

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {'username':username}).fetchall()

        print(rows)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id_username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """"Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Submit a username
        username = request.form.get("username")
        if not username:
            return apology("por favor, ingrese nombre de usuario", 400)

        # Submit password HASH
        password = request.form.get("password")
        if not password:
            return apology("por favor, ingrese contraseña",400)

        # Verify password 
        ver_password = request.form.get("confirmation")

        # Query database for username
        if password == ver_password:
            usuario = db.execute("SELECT * FROM users WHERE username=:username", {'username':username}).fetchall()
            if len(usuario) != 0 : 
                return apology("El usuario ya existe!", 403)
            try:
                rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", {'username':username, 'hash':generate_password_hash(password)})
                db.commit()
                #session["user_id"] = rows
            except:
                return apology("!El usuario ya existe!", 400)
                
            # Redirect user to home page
            return redirect("/")

        else:
            return apology("tu contraseña no coincide", 400)
    # User reached route via GET (as by clicking a link or via redirect) 
    else: 
        return render_template("register.html")

# if __name___ == '__main__':
   # app.run()