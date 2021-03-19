from typing import NoReturn, Union

from flask import Blueprint, redirect, render_template, request, url_for

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Character, Location

bp = Blueprint("characters", __name__, url_prefix="/characters")


def get_char(slug: str) -> Union[Character, NoReturn]:
    return Character.objects.get_or_404(slug__iexact=slug)


@bp.route("/")
@bp.route("/all")
def char_list():
    chars = Character.objects
    return render_template("characters/list.html", chars=chars)


@bp.route("/<slug>")
def char_detail(slug):
    char = get_char(slug)
    char.notes = render_markdown(char.notes)
    return render_template("characters/detail.html", char=char)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def char_new():
    if request.method == "POST":
        err = ""
        if request.form.get("name") is None:
            flash("Character name is required.")
            return redirect(url_for("characters.char_new"))
        char = Character(name=request.form["name"], notes=request.form.get("notes"))
        char.save()
        return redirect(url_for("characters.char_detail", slug=char.slug))
    locs = Location.objects
    return render_template("characters/new.html", locs=locs)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def char_edit(slug):
    char = get_char(slug)
    if request.method == "POST":
        if request.form.get("name") and char.name != request.form["name"]:
            char.name = request.form["name"]
        if request.form.get("notes") and char.notes != request.form["notes"]:
            char.notes = request.form["notes"]
        if request.form.get("location") != "null":
            char.location = Location.objects.get(slug=request.form.get("location"))
        char.save()
        return redirect(url_for("characters.char_detail", slug=slug))
    locs = Location.objects
    return render_template("characters/edit.html", char=char, locs=locs)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def char_delete(slug):
    char = get_char(slug)
    char.delete()
    return redirect(url_for("characters.char_list"))
