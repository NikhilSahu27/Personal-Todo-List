from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import sqlite3
from datetime import datetime

# create the app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("todo.db", check_same_thread=False)
db = con.cursor()
db.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY  AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)"
)
db.execute(
    "CREATE TABLE IF NOT EXISTS todo (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, complete BOOLEAN, user_id INTEGER, created_at DATETIME)"
)

# db.execute(
#     "INSERT INTO todo  (task, complete,user_id,created_at) VALUES (?,?,?,?)",
#     ("Complete this tutorial", False, 1, datetime.now()),
# )
res = db.execute("SELECT * FROM users")
con.commit()
print("Hello World")
print(res.fetchall())


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        )
        user = db.fetchone()
        if user:
            print(user)
            session["user_id"] = user[0]
            print(session["user_id"])
            flash("Logged in successfully!")
            return redirect("/index")
        else:
            return apology("Invalid username or password!", 403)
            # flash("Invalid username or password!")
            # return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password != confirm:
            return apology("Passwords do not match!", 403)
            # flash("Passwords do not match!")
            # return render_template("register.html")
        temp = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        if temp.fetchone():
            return apology("Username already exists!", 403)
            # flash("Username already exists!")
            # return render_template("register.html")

        db.execute(
            "INSERT INTO users  (username, password) VALUES (?,?)", (username, password)
        )
        con.commit()
        flash("Registered successfully!")
        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")


@app.route("/index")
def index():
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    else:
        fal = db.execute(
            "SELECT * FROM todo WHERE user_id = ? AND complete=False ORDER BY created_at DESC ",
            (session["user_id"],),
        )
        fal = fal.fetchall()
        # for i in fal:
        #     print(i[1])

        name = db.execute(
            "SELECT username FROM users WHERE id = ?", (session["user_id"],)
        )
        name = name.fetchone()

        con.commit()

        return render_template("index.html", fal=fal, name=name)


@app.route("/add", methods=["POST", "GET"])
def add():
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    elif request.method == "GET":
        name = db.execute(
            "SELECT username FROM users WHERE id = ?", (session["user_id"],)
        )
        name = name.fetchone()

        con.commit()
        return render_template("add.html", name=name)
    else:
        task = request.form.get("task")
        if task == "":
            return apology("Task cannot be empty!", 403)
            # flash("Task cannot be empty!")
            # return render_template("add.html")
        db.execute(
            "INSERT INTO todo (task, complete, user_id, created_at) VALUES (?,?,?,?)",
            (task, False, session["user_id"], datetime.now()),
        )
        con.commit()
        return redirect(url_for("index"))


@app.route("/done/<id>")
def done(id):
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    else:
        db.execute("UPDATE todo SET complete = True WHERE id = ?", (id,))
        con.commit()
        return redirect(url_for("index"))


@app.route("/completed")
def completed():
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    else:
        turu = db.execute(
            "SELECT * FROM todo WHERE user_id = ? AND complete=True ORDER BY created_at DESC ",
            (session["user_id"],),
        )
        turu = turu.fetchall()
        print(f"turu, {turu}!")
        name = db.execute(
            "SELECT username FROM users WHERE id = ?", (session["user_id"],)
        )
        name = name.fetchone()

        con.commit()
        return render_template("completed.html", turu=turu, name=name)


if __name__ == "__main__":
    app.run(debug=False)
