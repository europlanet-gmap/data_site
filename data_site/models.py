from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func


class Tool:
    def __init__(self, display_name="Tool"):
        self.display_name = display_name

    def get_link(self, obj):
        raise NotImplementedError

    def is_allowed(self, obj):
        return NotImplementedError


class EditTool(Tool):
    def __init__(self):
        super(EditTool, self).__init__("Edit")

    def get_link(self, obj):
        return f"{obj.id}/update"

    def is_allowed(self, obj):
        return current_user == obj.creator

class ViewTool(Tool):
    def __init__(self):
        super(ViewTool, self).__init__("View")

    def get_link(self, obj):
        return f"{obj.id}/record"

    def is_allowed(self, obj):
        return True


class DataPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000)) # package name, should be enough to find out the url for downloading the package
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user who created the dataset
    creator = db.relationship("User") # allows to access creator as an User instance
    body = db.Column(db.String(1500000))

    @property
    def editable(self):
         return current_user == self.creator

    @property
    def edit_url(self):
        return f"{self.id}/update"

    @property
    def tools(self):
        return [ViewTool(), EditTool()]




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True) # not needed for now but we might want to add it
    password_hash = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    location = db.Column(db.String(150))
    packages = db.relationship('DataPackage') # so we can access a list of this user packages

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)