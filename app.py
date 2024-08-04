from flask import Flask, flash, url_for, render_template, request, session, redirect
from sqlalchemy import Enum
from sqlalchemy import or_
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_session import Session
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from modules import login_required, get_weather
import secrets
from flask import Flask, render_template, request, jsonify
from flask import jsonify
import requests


app = Flask(__name__)
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hackathon.db"
app.config["SESSION_PERMANENT"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = secrets.token_hex(32)
app.static_folder = "static"  # Set the static folder to 'static'
app.static_url_path = "/static"


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# models definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.utcnow)


# routes definition
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # login required a
    name = "hanan"
    return render_template("index.html", name=name)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("name"):
            error_message = "Must provide name"
            return render_template("register.html", error=error_message)
        if not request.form.get("email"):
            error_message = "Error: Must provide email"
            return render_template("register.html", error=error_message)
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user:
            error_message = "Error: Email is already registered"
            return render_template("register.html", error=error_message)
        if not request.form.get("password") or not request.form.get("confirm"):
            error_message = "Must provide password"
            return render_template("register.html", error=error_message)
        if request.form.get("password") != request.form.get("confirm"):
            error_message = "Passwords don't match"
            return render_template("register.html", error=error_message)
        user = User(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password")),
            role="user",
            created_at=datetime.now(),
        )
        db.session.add(user)
        db.session.commit()
        flash("Register successful, Login to access your account!", "success")
        return redirect("/register")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            error_message = "Error: Must provide email"
            return render_template("login.html", error=error_message)

        elif not request.form.get("password"):
            error_message = "Error: Must provide password"
            return render_template("login.html", error=error_message)

        user = User.query.filter_by(email=request.form.get("email")).first()

        if not user or not check_password_hash(
            user.password, request.form.get("password")
        ):
            return render_template(
                "login.html", error="Error: Email and/or Password is incorrect! "
            )

        session["user_id"] = user.id
        session["user_name"] = user.name

        flash("Login successful!", "success")

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/weather", methods=["Post", "Get"])
def weather():
    data = request.json
    latitude = data["latitude"]
    longitude = data["longitude"]

    api_key = "2e6ed688a3309aea7d1e6b24845c94d9"  # Replace with your actual OpenWeatherMap API key
    weather_data = get_weather(latitude, longitude, api_key)
    if "error" in weather_data:
        return {"error": weather_data, "status": 500}
    else:
        return jsonify(weather_data)


if __name__ == "__main__":
    app.run()
