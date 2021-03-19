from typing import NoReturn, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import convert_markdown, slugify
from .documents import Character, Location

bp = Blueprint("characters", __name__, url_prefix="/characters")


def get_char(slug: str) -> Union[Character, NoReturn]:
    return Character.objects.get_or_404(slug__iexact=slug)


class CharacterForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    notes = TextAreaField()
    location = SelectField()


@bp.route("/")
@bp.route("/all")
def char_list():
    chars = Character.objects
    return render_template("characters/list.html", chars=chars)


@bp.route("/<slug>")
def char_detail(slug):
    char = get_char(slug)
    char.notes = convert_markdown(char.notes)
    return render_template("characters/detail.html", char=char)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def char_new():
    form = CharacterForm()
    form.location.choices = [("null", "---")] + [
        (loc.slug, loc.name) for loc in Location.objects()
    ]
    if request.method == "POST" and form.validate_on_submit():
        char = Character(name=form.name.data, notes=form.notes.data)
        if form.location.data != "null":
            char.location = Location.objects().get(slug__iexact=form.location.data)
        char.save()
        return redirect(url_for("characters.char_detail", slug=char.slug))

    return render_template("characters/new.html", form=form)


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
