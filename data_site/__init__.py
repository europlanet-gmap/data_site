import os

from flask import Flask

from data_site.blueprints import register_blueprints
from data_site.commands import register_commands

from data_site.extensions import create_database, register_extensions
from data_site.planmap_importer import init_app as planmap_importer_init
from data_site.error_handlers import register_errorhandlers
from data_site.settings import config

def create_app(config_name=None):
    """
    main app entry point
    :param config name: one of the names defined in settings.py
    :return: the created app
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')


    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config[config_name])

    # set_default_config(app)

    register_extensions(app)
    register_commands(app)
    register_blueprints(app)
    register_errorhandlers(app)
    create_database(app)

    if app.config["ENABLE_EXPERIMENTAL_COMPONENTS"]:
        print("registering dev routes")
        from data_site.dev_stuff import register_dev_routes
        register_dev_routes(app)



    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
