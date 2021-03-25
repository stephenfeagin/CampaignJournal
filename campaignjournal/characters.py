from datetime import datetime
from typing import List, NoReturn, Tuple, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Character, Location

bp = Blueprint("characters", __name__, url_prefix="/characters")


def get_char(slug: str) -> Union[Character, NoReturn]:
    return Character.objects.get_or_404(slug__iexact=slug)


def get_loc_choices() -> List[Tuple[str, str]]:
    return [("null", "---")] + [(loc.slug, loc.name) for loc in Location.objects()]


class CharacterForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    race = StringField()
    class_ = StringField("Class")
    notes = TextAreaField()
    location = SelectField()
    alive = RadioField(
        label="Alive or dead?", choices=(("a", "Alive"), ("d", "Dead")), default="a"
    )


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
    form = CharacterForm()
    form.location.choices = get_loc_choices()
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(char)
        if form.location.data != "null":
            char.location = Location.objects().get(slug__iexact=form.location.data)
        else:
            char.location = None
        char.save()
        return redirect(url_for("characters.char_detail", slug=char.slug))

    return render_template("characters/edit.html", pagetitle="New", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def char_edit(slug):
    char = get_char(slug)
    char_data = char.to_mongo()
    char_data["location"] = char.location.slug if char.location else "null"
    form = CharacterForm(data=char_data)
    form.location.choices = get_loc_choices()
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(char)
        if form.location.data != "null":
            char.location = Location.objects().get(slug__iexact=form.location.data)
        else:
            char.location = None
        char.save()
        return redirect(url_for("characters.char_detail", slug=slug))
    return render_template(
        "characters/edit.html", pagetitle="Edit", char=char, form=form
    )


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def char_delete(slug):
    char = get_char(slug)
    char.delete()
    return redirect(url_for("characters.char_list"))
