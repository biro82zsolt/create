# apps/performance/app.py

import os

from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash

from .routes import performance_bp
from .models import (
    db,
    Team,
    Coach,
    Player,
    AssessmentPeriod,
    Assessment,
)

from .services import (
    analyze_assessment,
    aggregate_assessments,
)
from .admin import init_admin
from .auth import login_coach, login_admin, is_authenticated, is_admin

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY"
)

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY nincs beállítva."
    )


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render / PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local development / SQLite
    db_path = os.path.join(BASE_DIR, "performance.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    print(f"Using database: {db_path}")


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ---------------------------------------------------------
# CREATE TABLES AND REGISTER BLUEPRINT
# ---------------------------------------------------------

with app.app_context():
    print("APP FILE:", os.path.abspath(__file__))
    print("DATABASE URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    db.create_all()
    app.register_blueprint(performance_bp)

init_admin(app)


# ---------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if login_coach(username, password):
            session.clear()
            session["auth_role"] = "coach"
            session["auth_username"] = username
            return redirect ("/performance/")

        flash("Hibás edzői felhasználónév vagy jelszó.", "error")

    return render_template("/performance/login.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if login_admin(username, password):
            session.clear()
            session["auth_role"] = "admin"
            session["auth_username"] = username
            return redirect ("/performance/admin/")

        flash("Hibás admin felhasználónév vagy jelszó.", "error")

    return render_template("/performance/admin_login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.before_request
def protect_non_admin_routes():
    endpoint = request.endpoint or ""
    path = request.path

    public = {"login", "admin_login", "logout", "admin_logout", "static"}
    if endpoint in public:
        return None

    if path.startswith("/admin"):
        return None

    if not is_authenticated():
        return redirect(
            url_for("login", next=request.path)
        )

    return None


# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

@app.get("/")
def index():
    return "Performance app OK"

if __name__ == "__main__":
    app.run(debug=True)