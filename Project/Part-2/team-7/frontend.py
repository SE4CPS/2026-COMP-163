from flask import Blueprint, render_template_string
from app import register_routes

frontend_bp = Blueprint("frontend", __name__)

with open("flowers.html", "r") as f:
    PAGE = f.read()

@frontend_bp.route("/")
def index():
    return render_template_string(PAGE)

register_routes(frontend_bp)
