import os

from flask import Flask, redirect

from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from loginpass import create_flask_blueprint, create_gitlab_backend

from .commands import init_commands

from .planmap_importer import init_app as planmap_importer_init


db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()
babel = Babel()

from .menu import MenuManager

menu_manager = MenuManager()

from .admin import AdminViews

admin = AdminViews()


from authlib.integrations.flask_client import OAuth

oauth= OAuth()
Gitlab = create_gitlab_backend("gitlab", "git.europlanet-gmap.eu")


def normalize_userinfo(client, data):
    return {
        'sub': str(data['id']),
        'name': data['name'],
        'email': data.get('email'),
        'preferred_username': data['username'],
        'profile': data['web_url'],
        'picture': data['avatar_url'],
        'website': data.get('website_url'),
        'is_admin': data.get("is_admin"),
        'gitlab_page' : data.get("profile"),
        'twitter': data.get("twitter"),
        "data": data
    }

Gitlab.OAUTH_CONFIG["userinfo_compliance_fix"] = normalize_userinfo


backends = [Gitlab]

#





# def handle_authorize(remote, token, user_info):
    # if token:
    #     save_token(remote.name, token)
    # if user_info:
    #     save_user(user_info)
    #     return user_page
    # raise some_error


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    bootstrap.init_app(app)

    babel.init_app(app)

    menu_manager.init_app(app)

    planmap_importer_init(app)

    init_commands(app)

    # init gitlab oauth integration
    app.config["GITLAB_CLIENT_ID"] =''
    app.config["GITLAB_CLIENT_SECRET"]=''

    oauth.init_app(app)

    # @app.route('/gitlab')
    # def index():
    #     tpl = '<li><a href="/login/{}">{}</a></li>'
    #     lis = [tpl.format(b.NAME, b.NAME) for b in backends]
    #     return '<ul>{}</ul>'.format(''.join(lis))
    from .auth import handle_authorize
    bp = create_flask_blueprint(backends, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='')





    db_path = os.path.join(app.instance_path, 'database.sqlite')
    print(db_path)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_PATH=db_path,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}")

    db.init_app(app)

    migrate.init_app(app, db)

    admin.init_app(app)

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

    @app.route("/testing")
    def testing():
        return redirect("admin.datapackage.new")



    return app


from .admin import DataPackageView


def create_database(app):
    from pathlib import Path
    if not Path(app.config["DATABASE_PATH"]).exists():
        db.create_all(app=app)
    else:
        print("Database already exists")


def create_test_admin(db):
    from .models import User, Role
    ad = User(username="admin", first_name="admin", last_name="De Admin" )
    ad.set_password("admin")
    # ad.role


