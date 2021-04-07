from typing import NoReturn, Union

from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Faction


bp = Blueprint("factions", __name__, url_prefix="/factions")


def get_faction(slug: str) -> Union[Faction, NoReturn]:
    return Faction.objects.get_or_404(slug__iexact=slug)


class FactionForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    notes = TextAreaField()


@bp.route("/")
@bp.route("/all")
def fac_list():
    facs = Faction.objects()
    return render_template("factions/list.html", facs=facs)


@bp.route("/<slug>")
def fac_detail(slug):
    fac = get_faction(slug)
    if fac.notes:
        fac.notes = render_markdown(fac.notes)
    return render_template("factions/detail.html", fac=fac)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def fac_new():
    form = FactionForm()
    if request.method == "POST" and form.validate_on_submit():
        fac = Faction(name=form.name.data, notes=form.notes.data)
        fac.save()
        return redirect(url_for("factions.fac_detail", slug=fac.slug))
    return render_template("factions/edit.html", pagetitle="New", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def fac_edit(slug):
    fac = get_faction(slug)
    fac_data = fac.to_mongo()
    form = FactionForm(data=fac_data)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(fac)
        fac.save()
        return redirect(url_for("factions.fac_detail", slug=slug))
    return render_template("factions/edit.html", pagetitle="Edit", fac=fac, form=form)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def fac_delete(slug):
    fac = get_faction(slug)
    fac.delete()
    return redirect(url_for("factions.fac_list"))