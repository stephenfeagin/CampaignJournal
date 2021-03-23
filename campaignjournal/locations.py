from typing import NoReturn, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Location, Character


bp = Blueprint("locations", __name__, url_prefix="/locations")


def get_loc(slug: str) -> Union[Location, NoReturn]:
    return Location.objects.get_or_404(slug__iexact=slug)


class LocationForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    notes = TextAreaField()


@bp.route("/")
@bp.route("/all")
def loc_list():
    locs = Location.objects
    return render_template("locations/list.html", locs=locs)


@bp.route("/<slug>")
def loc_detail(slug):
    loc = get_loc(slug)
    if loc.notes:
        loc.notes = render_markdown(loc.notes)
    chars = Character.objects(location=loc)
    return render_template("locations/detail.html", loc=loc, chars=chars)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def loc_new():
    form = LocationForm()
    if request.method == "POST" and form.validate_on_submit():
        loc = Location(name=form.name.data, notes=form.notes.data)
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=loc.slug))
    return render_template("locations/new.html", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def loc_edit(slug):
    loc = get_loc(slug)
    loc_data = loc.to_mongo()
    form = LocationForm(data=loc_data)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(loc)
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=slug))
    return render_template("locations/edit.html", loc=loc, form=form)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def loc_delete(slug):
    loc = get_loc(slug)
    loc.delete()
    return redirect(url_for("locations.loc_list"))