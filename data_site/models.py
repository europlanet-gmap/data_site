from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class DataPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000)) # package name, should be enough to find out the url for downloading the package
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user who created the dataset
    body = db.Column(db.String(1500000))


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