import functools
from typing import Callable

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from mongoengine import Document, DoesNotExist, StringField
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


class User(Document):
    username = StringField(max_length=64, required=True, unique=True)
    password = StringField(required=True)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if not user_id:
        g.user = None
    else:
        try:
            g.user = User.objects.get(id=str(user_id))
        except DoesNotExist:
            g.user = None


def login_required(view: Callable) -> Callable:
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password1")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif password != request.form.get("password2"):
            error = "Passwords do not match."
        elif User.objects(username__iexact=username).count():
            error = f"Username {username} is already in use."

        if error is None:
            user = User(username=username, password=generate_password_hash(password))
            user.save()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    # User is already logged in
    if g.user is not None:
        return redirect(url_for("core.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        try:
            user = User.objects.get(username__iexact=username)
        except DoesNotExist:
            error = "Incorrect username"
            user = None
        else:
            if not check_password_hash(user.password, password):
                error = "Incorrect password"

        if error is None:
            session.clear()
            session["user_id"] = str(user.id)
            flash(f"Welcome, {user.username}!")
            return redirect(url_for("core.index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("core.index"))
