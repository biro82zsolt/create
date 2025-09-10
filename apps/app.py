# combined-app/app.py
import os, sys
from importlib import import_module
from pathlib import Path
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# --- apps/ mappa felvétele az importútvonalra ---
REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = REPO_ROOT / "apps"
sys.path.insert(0, str(APPS_DIR))

# (opcionális) ha csak FLASK_SECRET_KEY van beállítva Renderen,
# az anthro app viszont SECRET_KEY-t olvas:
if "SECRET_KEY" not in os.environ and "FLASK_SECRET_KEY" in os.environ:
    os.environ["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

def load_flask_app(module_path: str):
    """
    Modul betöltése. Ha van create_app(), azt hívja; különben modul.app-ot vár.
    """
    m = import_module(module_path)
    if hasattr(m, "create_app"):
        return m.create_app()
    if hasattr(m, "app"):
        return m.app
    raise RuntimeError(f"Neither create_app() nor app found in {module_path}")

# --- Itt töltsd be a három appot ---
# Anthro: apps/anthro/app.py  ->  anthro.app
anthro_app = load_flask_app("anthro.app")

# Readiness: ha nálad apps/readiness/app.py, akkor readiness.app;
# ha más a név, írd át a modulútvonalat!
readiness_app = load_flask_app("readiness.app")

# Sportmotivation: apps/sportmotivation/app.py
sport_app = load_flask_app("sportmotivation.app")

# --- Root “héj” app csak gyökér/health célra ---
root = Flask(__name__)

@root.get("/")
def index():
    return "OK. Elérhető: /anthro , /readiness , /sportmotivation"

# --- Mountolás prefixek alá ---
application = DispatcherMiddleware(root, {
    "/anthro": anthro_app,
    "/readiness": readiness_app,
    "/sportmotivation": sport_app,
})

# Gunicorn ezt a nevet keresi:
app = application
