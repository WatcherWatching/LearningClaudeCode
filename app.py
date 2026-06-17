import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import create_user, get_db, init_db, seed_db

app = Flask(__name__)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not name or len(name) > 80:
            return render_template(
                "register.html", error="Name is required (max 80 characters)."
            ), 400
        if "@" not in email or "." not in email:
            return render_template(
                "register.html", error="Please enter a valid email address."
            ), 400
        if len(password) < 8:
            return render_template(
                "register.html", error="Password must be at least 8 characters."
            ), 400

        password_hash = generate_password_hash(password)

        try:
            create_user(name, email, password_hash)
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="An account with that email already exists.",
            ), 409

        return redirect(url_for("login", registered=1))

    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"



@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5002)
