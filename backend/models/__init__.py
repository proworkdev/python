from mongoengine import *


class Template(Document):
    identifier = StringField(required=True, unique=True)
    title = StringField()
    type = IntField(required=True, max_value=10)
    filename = StringField(required=True)
    bindings = DictField(required=True)
    edit_zone = ListField(required=True)
    colorizable = DictField()
    displacement_map = DictField()


class ColorizedTemplate(Document):
    identifier = StringField(required=True, unique=False)
    is_preview = BooleanField(required=True)
    ratio = ListField()
    color = StringField(required=True, unique=False)
    filename_color = StringField(required=True)
    filename_white = StringField(required=True)
