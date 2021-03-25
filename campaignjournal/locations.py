from typing import List, NoReturn, Optional, Tuple, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Character, Location


bp = Blueprint("locations", __name__, url_prefix="/locations")


def get_loc(slug: str) -> Union[Location, NoReturn]:
    return Location.objects.get_or_404(slug__iexact=slug)


def get_loc_choices(loc: Optional[Location] = None) -> List[Tuple[str, str]]:
    if loc is None:
        objs = Location.objects()
    else:
        objs = Location.objects(pk__ne=loc.pk)
    return [("null", "---")] + [(l.slug, l.name) for l in objs]


class LocationForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    parent = SelectField("Parent Location")
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
    return render_template("locations/detail.html", loc=loc)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def loc_new():
    form = LocationForm()
    form.parent.choices = get_loc_choices()
    if request.method == "POST" and form.validate_on_submit():
        loc = Location()
        form.populate_obj(loc)
        if form.parent.data != "null":
            loc.parent = Location.objects().get(slug__iexact=form.parent.data)
        else:
            loc.parent = None
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=loc.slug))
    return render_template("locations/edit.html", pagetitle="New", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def loc_edit(slug):
    loc = get_loc(slug)
    loc_data = loc.to_mongo()
    form = LocationForm(data=loc_data)
    form.parent.choices = get_loc_choices(loc)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(loc)
        if form.parent.data != "null":
            loc.parent = Location.objects().get(slug__iexact=form.parent.data)
        else:
            loc.parent = None
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=slug))
    return render_template("locations/edit.html", pagetitle="Edit", loc=loc, form=form)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def loc_delete(slug):
    loc = get_loc(slug)
    loc.delete()
    return redirect(url_for("locations.loc_list"))
