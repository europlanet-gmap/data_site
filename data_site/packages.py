import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app, session
)


from flask_login import current_user
from markupsafe import Markup

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
from data_site.auth import login_required
from data_site import form
from .forms import SearchForm
from .models import DataPackage, User

from flask_paginate import Pagination, get_page_args
from flask_menu import register_menu
from .forms import PackageForm


packages = Blueprint('packages', __name__)


@packages.route('/packages', methods=["GET"])
@register_menu(packages, 'packages.list', 'Packages List', order=10, type="main")
def index():

    s = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'id')



    # sort = creation_date & direction = asc
    from sqlalchemy import asc, desc
    if direction =="desc":
        sf = desc
    else:
        sf = asc
    packs = DataPackage.query.order_by(sf(s)).all()

    from .tables import PackageItemTable


    table = PackageItemTable(packs)
    print(table)

    return render_template('packages/index.html', table=table)


def get_unique_values_for_form(field, label="planetary_body"):
    values = db.session.query(field.distinct().label(label)).filter(field != None).all()
    values = [b[0] for b in values]
    values.insert(0,"Any")
    return [[str(b), str(b).capitalize()] for b in values]


@packages.route('/all-packages/', methods=["GET", "POST"])
@register_menu(packages, 'packages.packs', 'Packages', order=0, type="main")
def all_packages():

    default_args ={"query":"", "body":"Any", "creator": "Any"}
    page = request.args.get('page', 1, type=int) # get the page number

    if request.method != 'POST' and "args" in session.keys(): # we are not submitting any new search criteria
        args = session['args'] # we retrieve the latest values
    else:
        session['args'] =default_args
        args = {}


    form = SearchForm(**args)


    from .models import DataPackage

    bodies= get_unique_values_for_form(DataPackage.planetary_body_id, label="planetary_body")
    form.set_bodies(bodies)

    creators = get_unique_values_for_form(User.username, label="username")
    form.set_creators(creators)

    q = DataPackage.query # set up the query

    if form.validate_on_submit(): # new submission -> save into session

        if form.reset.data:
            session["args"] = default_args # reset to default and reload
            return redirect(url_for("packages.all_packages"))

        session["args"] = request.form

    # extract filters
    query = session["args"]["query"]
    body = session["args"]["body"]
    creator = session["args"]["creator"]

    if query:
        q = q.filter(DataPackage.name.like('%' + query + '%'))

    if body != "Any":
        q = q.filter_by(planetary_body=body)

    if creator != "Any":
        q = q.join(DataPackage.creator, aliased=True) \
            .filter_by(username = creator)

    packs = q.paginate(page=page, per_page=12)
    pagination = Pagination(page=page, per_page=12, total=q.count(),
                            css_framework='bootstrap4', alignment="right")


    return render_template("packages/all_packages.html", packages=packs.items, spanning=4, search_form=form, pagination=pagination)


@packages.route("/<int:id>/record")
def view(id):

    from .models import DataPackage

    pack = DataPackage.query.filter_by(id=id).first()

    from markdown import markdown

    if pack.description is not None:
        body = pack.description
    else:
        body = "<h6> No description for this package </h6>"


    return render_template("packages/view.html", package_name=pack.name, description=Markup(body))

@packages.route('/create2', methods=('GET', 'POST'))
@register_menu(packages, 'user.create2', 'New Package 2', order=100, visible_when=lambda: current_user.is_authenticated)
@login_required
def create2():
    return redirect(url_for("datapackage.create_view"))


@packages.route('/create', methods=('GET', 'POST'))
@register_menu(packages, 'user.create', 'New Package', order=100, visible_when=lambda: current_user.is_authenticated)
@login_required
def create(values={'files':None, 'metadata':None}):
    # if request.method == 'POST':
    #     form_files = None
    #     form_metadata = None
    #     error = None
    #     if '_form_metadata' in request.form:
    #         _form = request.form.copy()
    #         _form.pop('_form_metadata')
    #         errors = []
    #         try:
    #             form_parsed = form.parse(_form)
    #             print(form_parsed)
    #             form_ok = form.validate(form_parsed, errors)
    #             print(f"Form ok {form_ok}")
    #         except Exception as err:
    #             raise err
    #         else:
    #             values['metadata'] = form_parsed
    #         if  form_ok is not None:
    #             assert errors, errors
    #             [ flash(e) for e in errors ]
    #         else:
    #             flash('success')
    #
    #             from .models import DataPackage
    #
    #             pack = DataPackage(name=form_parsed["gmap_id"], creator_id=current_user.id)
    #             from . import db
    #             db.session.add(pack)
    #             db.session.commit()
    #
    #             # db = get_db()
    #             # db.execute(
    #             #     'INSERT INTO post (title, body, author_id)'
    #             #     ' VALUES (?, ?, ?)',
    #             #     (title, body, g.user['id'])
    #             # )
    #             # db.commit()
    #             return redirect(url_for('index'))
    #     else:
    #         assert '_form_upload' in request.form
    #         # _form = request.form.copy()
    #         # _form.pop('_form_upload')
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('No file selected')
    #             return redirect(request.url)
    #         file = request.files['file']
    #         # if user does not select file, browser also
    #         # submit an empty part without filename
    #         if file.filename == '':
    #             flash('No file selected')
    #             return redirect(request.url)
    #         if file and form.allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             localpath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    #             file.save(localpath)
    #             values['files'] = values['files'] + [filename] if values['files'] else [filename]
    #
    # return form.render(metadata=values['metadata'], files=values['files'])
    form = PackageForm()
    if request.method == 'GET':
        return render_template('packages/create.html', form=form)


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@packages.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    flash(f"Tring to modify package {id}", "info")
    return redirect(url_for('packages.index'))
    post = get_post(id)




    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('packages.index'))

    return render_template('packages/update.html', post=post)


@packages.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('packages.index'))
