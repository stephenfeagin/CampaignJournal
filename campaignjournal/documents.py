from datetime import datetime
from typing import List, NoReturn

from flask_mongoengine import Document
from mongoengine import DateTimeField, ListField, ReferenceField, StringField

from .core import slugify


class BaseDocument(Document):
    name = StringField(required=True)
    slug = StringField()
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    meta = {"abstract": True}

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.created:
            self.created = datetime.utcnow()
        self.updated = datetime.utcnow()
        super(Document, self).save(*args, **kwargs)


class Character(BaseDocument):
    name = StringField(required=True, unique=True, max_length=64)
    location = ReferenceField("Location")
    notes = StringField()
    alive = StringField(choices=(("a", "alive"), ("d", "dead")))

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
