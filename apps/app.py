# apps/app.py
import os, sys
from pathlib import Path
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# --- importútvonal: vegyük fel az apps/ könyvtárat ---
REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
sys.path.insert(0, str(APPS_DIR))

# --- importáld a három meglévő appot ---
# VÁLTOZAT A) ha van create_app():
anthro.app import create_app as create_anthro
# from readiness.app import create_app as create_readiness
# from sportmotivation_render.app import create_app as create_sport
# anthro_app = create_anthro()
# readiness_app = create_readiness()
# sport_app = create_sport()

# VÁLTOZAT B) ha modul-szintű 'app' van:
from anthro.app import app as anthro_app
from readiness.app import app as readiness_app
from sportmotivation.app import app as sportmotivation_app

# --- egy pici "root" app csak a főoldalra/health-re ---
root = Flask(__name__)
@root.get("/")
def index():
    return "OK. Elérhető: /anthro , /readiness , /sportmotivation"

# --- itt rakjuk őket egymás alá prefixszel ---
application = DispatcherMiddleware(root, {
    "/anthro": anthro_app,
    "/readiness": readiness_app,
    "/sportmotivation": sportmotivation_app,
})

# Gunicorn ezt a nevet keresi:
app = application
