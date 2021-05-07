from authlib.integrations.flask_client import OAuth
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from data_site.admin import AdminViews
from data_site.menu import MenuManager
from data_site.static_pages import Pages
from data_site.planmap_importer import init_app as planmap_importer_init


"""
All extensions external or internal should be initialized here
Access to extensions in various parts of the app can be done by 
from data_site.extensions import ..
"""

db = SQLAlchemy()
admin = AdminViews()
babel = Babel()
bootstrap = Bootstrap()
csrf = CSRFProtect()
menu_manager = MenuManager()
migrate = Migrate()
pages = Pages()
login_manager = LoginManager()
mail = Mail()
oauth = OAuth()


def create_database(app):
    print("verify presence of db")
    from pathlib import Path
    if not Path(app.config["DATABASE_PATH"]).exists():
        db.create_all(app=app)
    else:
        print("Database already exists")


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
    mail.init_app(app)
    planmap_importer_init(app)

    oauth.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)

    migrate.init_app(app, db)
    admin.init_app(app)
    menu_manager.init_app(app)
    login_manager.init_app(app)
    pages.init_app(app)


@login_manager.user_loader
def load_user(id):
    # note: this import should remain here to avoid circular imports
    from data_site.models import User
    return User.query.get(int(id))


class GuestUser(AnonymousUserMixin):
    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = GuestUser
login_manager.login_view = 'auth.login'
