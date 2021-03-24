import urllib
from datetime import datetime

from flask import Blueprint, render_template

bp = Blueprint("core", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


def slugify(x: str) -> str:
    dashes = x.replace(" ", "-").lower()
    return urllib.parse.quote(dashes)


@bp.add_app_template_filter
def datetimeformat(dt: datetime) -> str:
    try:
        result = dt.strftime("%m/%d/%Y")
    except AttributeError:
        result = "<N/A>"
    return result
