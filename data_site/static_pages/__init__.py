from flask import Blueprint, render_template, current_app, send_from_directory, url_for, redirect
from flask.cli import with_appcontext
from flask_flatpages import FlatPages
from flask_mdeditor import MDEditor, MDEditorField
from flask_menu import current_menu
from flask_pagedown import PageDown
from wtforms.validators import DataRequired

pages = Blueprint("static_pages", __name__, template_folder="templates")
from docutils.core import publish_parts
from flask_flatpages import FlatPages

from .markdown_processing import md_renderer

def register_menu_entries():
    """
    automatically registere the pages as menu entries depending on their "yaml-style" top-page metadata
    expected metadata of type:
    category: Documentation.Subtopic  will be mapped to a nested menu Documentation->Subtopic

    this method is then registered as a before_first_request_funcs for the app
    :return: None
    """
    paths = {}
    for p in current_app.extensions["pages"].pages:
        if "category" in p.meta.keys():
            cat = p.meta["category"]

            tt = current_menu

            for subcat in cat.split("."):
                tt = tt.submenu(subcat)
                tt._text = subcat
                tt.type = "main"
                tt._order = 10

            tt = tt.submenu(p.meta['title'] )
            tt._text = p.meta['title']
            paths[p] = p.path

            def generate_method():
                url = p.path
                return lambda: dict(page_path=url)

            tt._endpoint_arguments_constructor = generate_method()
            tt._endpoint = "static_pages.getpage"

class Pages(object):
    """
    Utility object that handles most of the stuff related to static pages
    """
    def init_app(self, app):
        self.pages = FlatPages(app)
        app.extensions["pages"] = self
        app.register_blueprint(pages, url_prefix="/")

        app.config["FLATPAGES_EXTENSION"] = [".md"]
        app.config["FLATPAGES_ROOT"] = "static/pages"
        app.config["FLATPAGES_MARKDOWN_EXTENSIONS"]= ['codehilite', 'tables']
        app.config['FLATPAGES_HTML_RENDERER'] = md_renderer

        app.config["FLATPAGES_EXTENSION_CONFIGS"] = {}

        # self.register_menu_entries()
        app.before_first_request_funcs.append(register_menu_entries)

        # self.pagedown = PageDown(app)
        import os
        self.mdeditor = MDEditor(app)
        app.config['MDEDITOR_FILE_UPLOADER'] = os.path.join("static",
                                                            'uploads')
        app.config["MDEDITOR_LANGUAGE"] = 'en'

        app.config["MDEDITOR_HEIGHT"] = 800
    # def register_menu_entries(self):
    #     for p in self.pages:
    #         if "category" in p.meta.keys():
    #             tt = current_menu.submenu(p.category)
    #             tt._text = "Documentation"
    #             tt.type = "main"
    #             tt._order = 0
    #
    #             print("adding page to menu")


@pages.route("/pages/<path:page_path>")
@pages.route("/pages/<path:page_path>.md")
def getpage(page_path):
    print(f"args --> {page_path}")

    from .. import pages
    p  = pages.pages.get(page_path)


    if p:
        print(f"--> page {p}")
        print(f"________ {dir(p)}")

        els = [a for a in dir(p) if not a.startswith('__') and not callable(getattr(p, a))]
        for el in els:
            print(getattr(p, el))

        return render_template("page.html", page = p)

    else:

        return send_from_directory('static/pages', page_path)

from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField

class PageDownFormExample(Form):
    """A simple page edit form"""
    content = MDEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Save')




@pages.route("/pages/edit/<path:page_path>", methods=["GET", "POST"])
@pages.route("/pages/edit/<path:page_path>.md", methods=["GET", "POST"])
def editpage(page_path):
    form = PageDownFormExample()

    from .. import pages
    page = pages.pages.get(page_path)
    if page:
        form.content.data = page.body

    else:
        return redirect(url_for("static_pages.getpage", page_path=page_path))

    if form.validate_on_submit():
        text = form.content.data
        print("edited")
        # do something interesting with the Markdown text

        return redirect(url_for("static_pages.getpage", page_path=page_path))

    return render_template('edit_page.html', form=form, title=page_path)



