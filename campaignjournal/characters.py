from datetime import datetime
from typing import List, NoReturn, Tuple, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import convert_markdown, slugify
from .documents import Character, Location

bp = Blueprint("characters", __name__, url_prefix="/characters")


def get_char(slug: str) -> Union[Character, NoReturn]:
    return Character.objects.get_or_404(slug__iexact=slug)


def get_loc_choices() -> List[Tuple[str, str]]:
    return [("null", "---")] + [(loc.slug, loc.name) for loc in Location.objects()]


class CharacterForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    notes = TextAreaField()
    location = SelectField()
    alive = BooleanField(
        label="Alive?", description="Is this character alive?", default=True
    )


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
    form.location.choices = get_loc_choices()
    if request.method == "POST" and form.validate_on_submit():
        char = Character(
            name=form.name.data, notes=form.notes.data, alive=form.alive.data
        )
        if form.location.data != "null":
            char.location = Location.objects().get(slug__iexact=form.location.data)
        char.save()
        return redirect(url_for("characters.char_detail", slug=char.slug))

    return render_template("characters/new.html", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def char_edit(slug):
    char = get_char(slug)
    char_data = char.to_mongo()
    char_data["location"] = char.location.slug if char.location else "null"
    form = CharacterForm(data=char_data)
    form.location.choices = get_loc_choices()
    if request.method == "POST" and form.validate_on_submit():
        if char.name != form.name.data:
            char.name = form.name.data
        if char.notes != form.notes.data:
            char.notes = form.notes.data
        if form.location.data != "null":
            if char.location and char.location.slug != form.location.data:
                char.location = Location.objects().get(slug__iexact=form.location.data)
        else:
            char.location = None
        if char.alive != form.alive.data:
            char.alive = form.alive.data
        char.save()
        return redirect(url_for("characters.char_detail", slug=slug))
    return render_template("characters/edit.html", char=char, form=form)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def char_delete(slug):
    char = get_char(slug)
    char.delete()
    return redirect(url_for("characters.char_list"))
