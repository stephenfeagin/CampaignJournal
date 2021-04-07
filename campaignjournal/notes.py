from datetime import datetime
from typing import NoReturn, Union

from flask import Blueprint, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import InputRequired

from .auth import login_required
from .core import slugify
from .doclinks import render_markdown
from .documents import Note


bp = Blueprint("notes", __name__, url_prefix="/notes")


def get_note(slug: str) -> Union[Note, NoReturn]:
    return Note.objects.get_or_404(slug__iexact=slug)


class NoteForm(FlaskForm):
    name = StringField(validators=[InputRequired()])
    notes = TextAreaField()


@bp.route("/")
@bp.route("/all")
def note_list():
    nts = Note.objects()
    return render_template("notes/list.html", nts=nts)


@bp.route("/<slug>")
def note_detail(slug):
    nt = get_note(slug)
    if nt.notes:
        nt.notes = render_markdown(nt.notes)
    return render_template("notes/detail.html", nt=nt)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def note_new():
    form = NoteForm()
    if request.method == "POST" and form.validate_on_submit():
        nt = Note(name=form.name.data, notes=form.notes.data)
        nt.save()
        return redirect(url_for("notes.note_detail", slug=nt.slug))
    return render_template("notes/edit.html", pagetitle="New", form=form)


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def note_edit(slug):
    nt = get_note(slug)
    nt_data = nt.to_mongo()
    form = NoteForm(data=nt_data)
    if request.method == "POST" and form.validate_on_submit():
        form.populate_obj(nt)
        nt.save()
        return redirect(url_for("notes.note_detail", slug=slug))
    return render_template("notes/edit.html", pagetitle="Edit", nt=nt, form=form)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def note_delete(slug):
    nt = get_note(slug)
    nt.delete()
    return redirect(url_for("notes.note_list"))
