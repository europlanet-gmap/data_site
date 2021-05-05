# simple admin iface
from flask_admin import Admin
from flask_admin.form import rules
from wtforms import PasswordField

from .models import User, DataPackage, PlanetaryBody, Role, Permission
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

from data_site import db
from wtforms import validators


class AdminViewBase(ModelView):
    column_hide_backrefs = False


class UserView(AdminViewBase):
    """Flask user model view."""
    column_filters = ("email", "username")
    form_excluded_columns = ('password_hash')

    form_extra_fields = {
        'password': PasswordField('Password', [validators.DataRequired()])
    }

    form_args = dict(
        username=dict(validators=[validators.DataRequired()]),
        email=dict(validators=[validators.DataRequired()])
    )

    def on_model_change(self, form, User, is_created):
        if form.password.data is not None:
            User.set_password(form.password.data)

    def on_form_prefill(self, form, id):
        form.password.data = '********'
        form.username.data = ""

from wtforms import TextAreaField
from wtforms.widgets import TextArea

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class DataPackageView(AdminViewBase):
    pass
    # # create_modal = True
    # column_list = ("id", "name", "creation_date", "description", "planetary_body", "thumbnail_url")
    # column_searchable_list = ("name", "description")
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']

    form_overrides = {
        'description': CKTextAreaField
    }



class PlanetaryBodyView(AdminViewBase):
    column_list = ('name', "is_planet", "packages")



class RoleView(AdminViewBase):
    pass


class PermissionView(AdminViewBase):
    pass


class AdminViews(object):
    def init_app(self, app):
        self.admin = Admin(name='data_site', template_mode='bootstrap4')
        self.admin.init_app(app)

        mv = UserView(User, db.session, category="Users")

        self.admin.add_view(mv)

        mv = DataPackageView(DataPackage, db.session, category="Packages")

        self.admin.add_view(mv)

        mv = PlanetaryBodyView(PlanetaryBody, db.session, category="Packages")

        self.admin.add_view(mv)

        mv = RoleView(Role, db.session, category="Users")
        self.admin.add_view(mv)

        mv = RoleView(Permission, db.session, category="Users")
        self.admin.add_view(mv)
