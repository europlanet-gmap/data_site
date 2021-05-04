from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_login.signals import user_logged_in, user_logged_out
from flask_menu import Menu, current_menu
from markupsafe import Markup

# menu = Blueprint('menu', __name__)


menu = Blueprint("menu", __name__, template_folder="templates")


@menu.add_app_template_global
def render_main_menu():
    return Markup(render_template("main_menu.html", type="main"))


@menu.add_app_template_global
def render_user_menu():
    return Markup(render_template("user_menu.html", type="user"))


@menu.route('menu')
@login_required
def a():
    return render_template("main_menu.html", type="main")


@menu.route('menu/auth')
@login_required
def b():
    return render_template("user_menu.html", type="user")


class MenuManager(object):
    def __init__(self):
        self.menu = Menu()

    def init_app(self, app):
        self.menu.init_app(app)
        app.menu = self
        # app.cli.add_command(do_work)
        app.before_first_request_funcs.append(register_external_menu_items)

        app.register_blueprint(menu, url_prefix='/')

        # @user_logged_in.connect_via(app)
        # def _after_login_hook(sender, **extra):
        #     print("--> exec after login hook")
        #     tt = current_menu.submenu("user")
        #     tt._text = current_user.username
        #
        # @user_logged_out.connect_via(app)
        # def _after_logout_hook(sender, **extra):
        #     tt = current_menu.submenu("user")
        #     tt._text = "User"


def register_external_menu_items():
    tt = current_menu.submenu("external")
    tt._text = "External Links"
    tt._order = 1000
    tt.type = "main"

    tt = current_menu.submenu("user")
    tt._text = "User"
    tt.type = "user"

    tt = current_menu.submenu("packages")
    tt._text = "Packages"
    tt.type = "main"
    tt._order = 0

    # tt = current_menu.submenu("external.planmap")
    # tt._text = "Planmap stuff"
    # tt.type = "main"

    # tt = current_menu.submenu("external.gmap")
    # tt._text = "Gmap stuff"
    # tt.type = "main"


    tt = current_menu.submenu("external.gmap_stuff")
    tt.type = "main"
    tt._text ="gmap stuff"

    tt = current_menu.submenu("external.gmap_stuff.gmap")
    tt._external_url = "https://europlanet-gmap.eu"

    tt._text = "GMAP Website"
    tt.type = "main"

    tt = current_menu.submenu("external.planmap")
    tt._external_url = "https://planmap.eu"
    tt._text = "Planmap Website"
    tt.type = "main"
    # current_menu.register(external_url="https://planmep.eu", text="Planmap", type="main")
