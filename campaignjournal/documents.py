from datetime import datetime
from typing import List

from flask_mongoengine import Document
from mongoengine import DateTimeField, ListField, ReferenceField, StringField

from .core import slugify


class Character(Document):
    name = StringField(required=True, unique=True, max_length=64)
    slug = StringField()
    location = ReferenceField("Location")
    notes = StringField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Character, self).save(*args, **kwargs)

    def __repr__(self):
        return f"<Character: {self.name}>"


class Location(Document):
    name = StringField(required=True, unique=True, max_length=64)
    slug = StringField()
    parent = ReferenceField("self")
    notes = StringField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Location, self).save(*args, **kwargs)

    def get_children(self):
        return Location.objects(parent=self)

    def get_characters(self):
        return Character.objects.get(location=self)

    def __repr__(self):
        return f"<Location: {self.name}>"


class Note(Document):
    name = StringField(required=True, unique=True, max_length=64)
    slug = StringField()
    note_type = StringField(default="General", choices=("General",))
    notes = StringField()
    created = DateTimeField(default=datetime.utcnow, required=True)
    updated = DateTimeField(default=datetime.utcnow, required=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.updated = datetime.utcnow()
        return super(Note, self).save(*args, **kwargs)