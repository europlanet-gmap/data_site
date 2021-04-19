import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app
)
from flask_login import current_user

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from . import db
from data_site.auth import login_required
from data_site import form
from .models import DataPackage

packages = Blueprint('packages', __name__)


@packages.route('/packages', methods=["GET"])
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

@packages.route("/<int:id>/record")
def view(id):
    flash(f"This page must be implemented, but should show properties of package {id}")
    return render_template("base.html")


@packages.route('/create', methods=('GET', 'POST'))
@login_required
def create(values={'files':None, 'metadata':None}):
    if request.method == 'POST':
        form_files = None
        form_metadata = None
        error = None
        if '_form_metadata' in request.form:
            _form = request.form.copy()
            _form.pop('_form_metadata')
            errors = []
            try:
                form_parsed = form.parse(_form)
                print(form_parsed)
                form_ok = form.validate(form_parsed, errors)
                print(f"Form ok {form_ok}")
            except Exception as err:
                raise err
            else:
                values['metadata'] = form_parsed
            if  form_ok is not None:
                assert errors, errors
                [ flash(e) for e in errors ]
            else:
                flash('success')

                from .models import DataPackage

                pack = DataPackage(name=form_parsed["gmap_id"], creator_id=current_user.id)
                from . import db
                db.session.add(pack)
                db.session.commit()

                # db = get_db()
                # db.execute(
                #     'INSERT INTO post (title, body, author_id)'
                #     ' VALUES (?, ?, ?)',
                #     (title, body, g.user['id'])
                # )
                # db.commit()
                return redirect(url_for('index'))
        else:
            assert '_form_upload' in request.form
            # _form = request.form.copy()
            # _form.pop('_form_upload')
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file selected')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No file selected')
                return redirect(request.url)
            if file and form.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                localpath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(localpath)
                values['files'] = values['files'] + [filename] if values['files'] else [filename]

    return form.render(metadata=values['metadata'], files=values['files'])


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
