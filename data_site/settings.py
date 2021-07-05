import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = "europlanet.gmap@gmail.com"

    MAIL_PREPEND = "[GMAP DATA]"

    GITLAB_URL = "https://git.europlanet-gmap.eu/"
    GITLAB_CLIENT_ID = os.environ.get("GITLAB_CLIENT_ID")
    GITLAB_CLIENT_SECRET = os.environ.get("GITLAB_CLIENT_SECRET")

    SECRET_KEY=os.environ.get("DATA_SITE_SECRET_KEY", "empty")

    SQLALCHEMY_DATABASE_URI = f"{prefix}{os.path.join(basedir, 'instance',  'database.sqlite')}"
    DATABASE_PATH = f"{os.path.join(basedir, 'instance',  'database.sqlite')}"

    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')

    ALLOWED_EXTENSIONS = {'tif', 'tiff', 'zip', 'gpkg', 'pdf', 'png', 'jpg'}

    MAIN_PAGE_LAST_ITEMS_NUMBER = 12
    ENABLE_EXPERIMENTAL_COMPONENTS = False

class DevelopmentConfig(BaseConfig):
    ENABLE_EXPERIMENTAL_COMPONENTS =True


class TestingConfig(BaseConfig):
    TESTING = True
    # WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database


class ProductionConfig(BaseConfig):
    pass
    """just an example from albumy. not intended for use"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        prefix + os.path.join(basedir, 'data.db'))




config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}