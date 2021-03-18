from datetime import datetime
from typing import List, NoReturn

from flask_mongoengine import Document
from mongoengine import (
    BooleanField,
    DateTimeField,
    ListField,
    ReferenceField,
    StringField,
)

from .core import slugify


class BaseDocument(Document):
    name = StringField(required=True)
    slug = StringField()
    created = DateTimeField(default=datetime.utcnow, required=True)
    updated = DateTimeField(default=datetime.utcnow, required=True)

    meta = {"abstract": True}

    def set_updated(self) -> NoReturn:
        self.updated = datetime.utcnow()

    def set_slug(self) -> NoReturn:
        if not self.slug:
            self.slug = slugify(self.name)

    @classmethod
    def pre_save_post_validate(cls, sender, document, **kwargs) -> NoReturn:
        set_updated(document)
        set_slug(document)


class Character(BaseDocument):
    name = StringField(required=True, unique=True, max_length=64)
    location = ReferenceField("Location")
    notes = StringField()
    dead = BooleanField(default=False)

    meta = {"ordering": ["name"]}

    def __repr__(self):
        return f"<Character: {self.name}>"


class Location(BaseDocument):
    name = StringField(required=True, unique=True, max_length=64)
    parent = ReferenceField("self")
    notes = StringField()

    meta = {"ordering": ["name"]}

    def get_children(self):
        return Location.objects(parent=self)

    def get_characters(self):
        return Character.objects.get(location=self)

    def __repr__(self):
        return f"<Location: {self.name}>"


class Note(BaseDocument):
    name = StringField(required=True, unique=True, max_length=64)
    note_type = StringField(default="General", choices=("General",))
    notes = StringField()

    meta = {"ordering": ["-updated"]}