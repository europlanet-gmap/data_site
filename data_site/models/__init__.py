from flask import current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash

from data_site.extensions import db
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


roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')

    def __repr__(self):
        return self.name

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', back_populates='role')
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')

    @staticmethod
    def get_role(name):
        role = Role.query.filter_by(name=name).first()
        if not role:
            flash(f"Debug: role {name} does not exists")
            return None
        return role

    @staticmethod
    def get_admin_role():
        return Role.get_role("Administrator")

    @staticmethod
    def init_default_roles():
        print("inizializing default roles")
        roles_permissions_map = {
            'User': ['UPLOAD', 'COMMENT'],
            'Moderator': ['UPLOAD', 'MODERATE', 'REVIEW'],
            'Administrator': ['UPLOAD', 'MODERATE', 'REVIEW', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()

    def __repr__(self):
        return self.name




class PlanetaryBody(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False, unique=True)
    is_planet = db.Column(db.Boolean())
    packages = db.relationship('DataPackage', back_populates='planetary_body', uselist=True)

    def __repr__(self):
        return self.name

    @staticmethod
    def get_unknwon_body():
        return PlanetaryBody.query.filter_by(name="unknown").first()

class DataPackageMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package = db.relationship("DataPackage", back_populates="pkg_metadata")

class DataPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000)) # package name, should be enough to find out the url for downloading the package
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user who created the dataset
    creator = db.relationship("User",  back_populates="packages") # allows to access creator as an User instance
    description = db.Column(db.String(1500000))
    # body_format = db.Column(db.String(20), default=None) # format of 'body' content, this will be used for rendering it
    planetary_body_id = db.Column(db.Integer, db.ForeignKey('planetary_body.id'))
    planetary_body = db.relationship("PlanetaryBody", back_populates="packages", lazy="joined")
    thumbnail_url =db.Column(db.String(1000))



    pkg_metadata_id =  db.Column(db.Integer, db.ForeignKey('data_package_metadata.id'))
    pkg_metadata = db.relationship("DataPackageMetadata", back_populates="package")

    @property
    def editable(self):
         return current_user == self.creator

    @property
    def edit_url(self):
        return f"{self.id}/update"

    @property
    def tools(self):
        return [ViewTool(), EditTool()]

    def __repr__(self):
        return self.name




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True) # not needed for now but we might want to add it
    password_hash = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    location = db.Column(db.String(150))
    gitlab_id = db.Column(db.Integer, unique=True)
    packages = db.relationship('DataPackage', back_populates="creator", lazy='dynamic') # so we can access a list of this user packages

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username

    def allow_admin(self):
        admin_role = Role.get_admin_role()
        if admin_role:
            self.role = admin_role

    @property
    def is_admin(self):

        admin_role = Role.get_admin_role()
        print(f"is admin called {admin_role}\n {self.role == admin_role}")
        return self.role == admin_role

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions

    def __repr__(self):
        return str(self.username)





