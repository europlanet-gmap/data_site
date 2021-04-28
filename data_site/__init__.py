import os

from flask import Flask
from flask_login import LoginManager, login_required
from flask_menu import register_menu
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from .planmap_importer import init_app as planmap_importer_init
# import planmap_importer
from flask_babel import Babel

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
# from flask_menu import Menu, register_menu, current_menu

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
babel = Babel()
admin = Admin(name='data_site', template_mode='bootstrap4')
# menu = Menu()

from .menu import MenuManager

menu_manager = MenuManager()



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    bootstrap.init_app(app)

    babel.init_app(app)

    menu_manager.init_app(app)

    planmap_importer_init(app)



    db_path = os.path.join(app.instance_path, 'database.sqlite')
    print(db_path)
    

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_PATH = db_path,
        SQLALCHEMY_DATABASE_URI= f"sqlite:///{db_path}")

    db.init_app(app)

    migrate.init_app(app, db)


    # simple admin iface
    admin.init_app(app)
    from .models import User, DataPackage

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(DataPackage, db.session))





    # menu.init_app(app)



    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import main
    app.register_blueprint(main.main, url_prefix="/")

    from . import auth
    app.register_blueprint(auth.auth, url_prefix='/')

    from . import packages
    app.register_blueprint(packages.packages, url_prefix='/')
    app.add_url_rule('/', endpoint='index')


    # database init
    from .models import DataPackage, User

    create_database(app)

    # logins management
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    _curdir = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(_curdir, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = {'tif', 'tiff', 'zip', 'gpkg', 'pdf', 'png', 'jpg'}
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


    return app





def create_database(app):
    from pathlib import Path
    if not Path(app.config["DATABASE_PATH"]).exists():
        db.create_all(app=app)
        print('Created Database!')

