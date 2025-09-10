from flask import Blueprint

readiness_bp = Blueprint("readiness", __name__, url_prefix="/readiness")

@readiness_bp.route("/")
def index():
    return "Readiness web running!"
