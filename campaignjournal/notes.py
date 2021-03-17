from datetime import datetime
from typing import NoReturn, Union

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .auth import login_required
from .core import convert_markdown, slugify
from .documents import Note

bp = Blueprint("notes", __name__, url_prefix="/notes")


def get_note(slug: str) -> Union[Note, NoReturn]:
    return Note.objects.get_or_404(slug__iexact=slug)


@bp.route("/")
@bp.route("/all")
def note_list():
    nts = Note.objects().order_by("-updated")
    for n in nts:
        n.notes = convert_markdown(n.notes)
    return render_template("notes/list.html", nts=nts)


@bp.route("/<slug>")
def note_detail(slug):
    nt = get_note(slug)
    if nt.notes:
        nt.notes = convert_markdown(nt.notes)
    return render_template("notes/detail.html", nt=nt)


@bp.route("/new", methods=("GET", "POST"))
@login_required
def note_new():
    if request.method == "POST":
        err = ""
        if request.form.get("name") is None:
            flash("Note name is required.")
            return redirect(url_for("notes.note_new"))
        nt = Note(
            name=request.form["name"],
            note_type=request.form.get("note_type"),
            notes=request.form.get("notes"),
        )
        nt.save()
        return redirect(url_for("notes.note_detail", slug=nt.slug))
    return render_template("notes/new.html")


@bp.route("/<slug>/edit", methods=("GET", "POST"))
@login_required
def note_edit(slug):
    nt = get_note(slug)
    if request.method == "POST":
        if request.form.get("name") and nt.name != request.form["name"]:
            nt.name = request.form["name"]
        if request.form.get("note_type") and nt.note_type != request.form["note_type"]:
            nt.note_type = request.form["note_type"]
        if request.form.get("notes") and nt.notes != request.form["notes"]:
            nt.notes = request.form["notes"]
        nt.save()
        return redirect(url_for("notes.note_detail", slug=slug))
    return render_template("notes/edit.html", nt=nt)


@bp.route("/<slug>/delete", methods=("POST",))
@login_required
def note_delete(slug):
    nt = get_note(slug)
    nt.delete()
    return redirect(url_for("notes.note_list"))
