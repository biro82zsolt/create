from flask import Blueprint

anthro_bp = Blueprint("anthro", __name__, url_prefix="/anthro")

@anthro_bp.route("/")
def index():
    return "Anthro web running!"
