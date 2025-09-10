import os, sys
from pathlib import Path
from flask import Flask

# --- importútvonal: felvesszük az apps/ könyvtárat a PYTHONPATH-ra ---
REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
sys.path.insert(0, str(APPS_DIR))

# --- blueprintek importja a három appból ---
from anthro import anthro_bp          # apps/anthro/__init__.py exportálja
from readiness import readiness_bp    # apps/readiness/__init__.py exportálja
from sportmotivation import sportmotivation_bp  # apps/sportmotivation/__init__.py exportálja

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    # blueprintek felvétele
    app.register_blueprint(anthro_bp)
    app.register_blueprint(readiness_bp)
    app.register_blueprint(sportmotivation_bp)

    @app.get("/")
    def root():
        return "OK: /anthro, /readiness, /sportmotivation elérhető."

    return app

app = create_app()
