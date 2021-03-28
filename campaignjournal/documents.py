import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, NoReturn, Optional

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
    class_ = StringField()
    race = StringField()
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
        return Character.objects(location=self)

    def descendant_tree(self) -> ET.Element:
        li = ET.Element("li")
        li.text = self.name
        children = self.get_children()
        if not children:
            return li
        ul = ET.SubElement(li, "ul")
        for child in children:
            ul.append(child.descendant_tree())
        return li

    @classmethod
    def location_tree(cls) -> Optional[ET.Element]:
        locs = cls.objects(parent=None)
        if not locs:
            return
        ul = ET.Element("ul")
        for loc in locs:
            ul.append(loc.descendant_tree())
        return ul

    def __repr__(self):
        return f"<Location: {self.name}>"


class Note(BaseDocument):
    name = StringField(required=True, unique=True, max_length=64)
    note_type = StringField(default="General", choices=("General",))
    notes = StringField()

    meta = {"ordering": ["-updated"]}
