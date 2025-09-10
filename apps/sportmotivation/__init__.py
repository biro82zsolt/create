from flask import Blueprint

sportmotivation_bp = Blueprint("sportmotivation", __name__, url_prefix="/sportmotivation")

@sportmotivation_bp.route("/")
def index():
    return "Sport motivation running!"
