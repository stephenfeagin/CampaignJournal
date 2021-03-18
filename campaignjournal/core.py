from datetime import datetime
import re
from typing import Dict, Union
import urllib

from flask import Blueprint, render_template, url_for
import markdown

bp = Blueprint("core", __name__)


def slugify(x: str) -> str:
    dashes = x.replace(" ", "-").lower()
    return urllib.parse.quote(dashes)


@bp.route("/")
def index():
    return render_template("index.html")


def match_to_url(m: re.Match) -> str:
    """
    match_to_url converts a regex Match object into a resolved URL
    """
    url_patterns = {
        "location": "locations.loc_detail",
        "character": "characters.char_detail",
        "npc": "characters.char_detail",
    }

    category, name, display = m.groups()
    if display is None:
        display = name

    url = url_patterns.get(category.lower())
    if url is None:
        return m.group()

    slug = slugify(name)
    full_url = url_for(url, slug=slug)
    markdown_link = f"[{display}]({full_url})"
    return markdown_link


def convert_markdown(text: str) -> str:
    """
    convert_link converts all of the supported wiki-style links in a text into resolved URLs
        and returns the entire text, markdownified
    """
    link_pattern = re.compile(r"\[\[([\w\s]+)\s?:\s?([\w\s]+):?([\w\s]+)?\]\]")
    replaced = link_pattern.sub(match_to_url, text)
    return markdown.markdown(replaced)


@bp.add_app_template_filter
def datetimeformat(dt: datetime) -> str:
    return dt.strftime("%m/%d/%Y")
