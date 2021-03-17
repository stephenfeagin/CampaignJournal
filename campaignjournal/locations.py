from typing import NoReturn, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .auth import login_required
from .core import convert_markdown, slugify
from .documents import Location, Character


bp = Blueprint("locations", __name__, url_prefix="/locations")


def get_loc(slug: str) -> Union[Location, NoReturn]:
    return Location.objects.get_or_404(slug__iexact=slug)


@bp.route("/")
@bp.route("/all")
def loc_list():
    locs = Location.objects
    return render_template("locations/list.html", locs=locs)


@bp.route("/<slug>")
def loc_detail(slug):
    loc = get_loc(slug)
    if loc.notes:
        loc.notes = convert_markdown(loc.notes)
    chars = Character.objects(location=loc)
    return render_template("locations/detail.html", loc=loc, chars=chars)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def loc_new():
    if request.method == "POST":
        err = ""
        if request.form.get("name") is None:
            flash("Location name is required.")
            return redirect(url_for("locations.loc_new"))
        loc = Location(name=request.form["name"], notes=request.form.get("notes"))
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=loc.slug))
    return render_template("locations/new.html")


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def loc_edit(slug):
    loc = get_loc(slug)
    if request.method == "POST":
        if request.form.get("name") and loc.name != request.form["name"]:
            loc.name = request.form["name"]
        if request.form.get("notes") and loc.notes != request.form["notes"]:
            loc.notes = request.form["notes"]
        loc.save()
        return redirect(url_for("locations.loc_detail", slug=slug))
    return render_template("locations/edit.html", loc=loc)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def loc_delete(slug):
    loc = get_loc(slug)
    loc.delete()
    return redirect(url_for("locations.loc_list"))