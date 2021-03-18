import os

from flask import Flask
from flask_mongoengine import MongoEngine
import markdown

from . import auth, characters, core, documents, locations, notes


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register mongodb
    app.config["MONGODB_HOST"] = os.environ.get("MONGODB_URI")
    db = MongoEngine()
    db.init_app(app)

    # register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(characters.bp)
    app.register_blueprint(core.bp)
    app.register_blueprint(locations.bp)
    app.register_blueprint(notes.bp)

    @app.context_processor
    def inject_documents():
        all_locs = documents.Location.objects()
        all_chars = documents.Character.objects()
        return dict(all_locs=all_locs, all_chars=all_chars)

    return app