from flask import Blueprint

bp = Blueprint("performance_v2", __name__)


@bp.route("/")
def index():
    return "<h1>Performance 2.0 működik</h1>"