import os
import json

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from flask_login import current_user

from markupsafe import Markup
from markdown import markdown, Markdown

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from data_site import db, form
from data_site.auth import login_required
from data_site.forms import PackageForm, UploadForm
from data_site.models import DataPackage


def flash_errors(form):
    """Flashes form errors"""
    try:
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                    ),
                    'error'
                )
    except:
        print("No errors found.")


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

    from data_site.tables import PackageItemTable
    table = PackageItemTable(packs)

    return render_template('packages/index.html', table=table)


@packages.route("/<int:id>/record")
def view(id):
    pack = DataPackage.query.filter_by(id=id).first()

    if pack.body is not None:
        body = pack.body
    else:
        body = "# No description for this package"

    body_js = json.loads(body)
    body_str = "|Field|Value|\n|:---|---:|\n"
    for key,value in body_js.items():
        field = key.replace('_',' ').capitalize()
        body_str += f"|{field}|{value}|\n"
    ashtml = markdown(body_str, extensions=['tables'])
    print(body_str)
    print(ashtml)
    return render_template("packages/view.html", package_name=pack.name, description=Markup(ashtml))


# session = {'files':None, 'fields':None}

def save_file(form_file):
    filename = secure_filename(form_file.filename)
    localpath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    form_file.save(localpath)
    return (filename, localpath)


def submit_package(form_data, files=None):
    data = {k:v for k,v in form_data.items()
                if k not in ('submit','csrf_token')}
    if files:
        data.update({'files':files})
    content = json.dumps(data)
    p = DataPackage(name=data['name'], creator_id=current_user.id,
                    planetary_body=data['target_body'],
                    body=content)
    db.session.add(p)
    db.session.commit()
    save_package(form_data, files)
    return p.id


import shutil
def save_package(meta, data):
    base_path = current_app.config['UPLOAD_FOLDER']
    pkg_path = os.path.join(base_path, meta['gmap_id'])
    os.makedirs(pkg_path, exist_ok=True)
    pkg_meta = os.path.join(pkg_path, 'meta.json')
    with open(pkg_meta, 'w') as fp:
        json.dump(meta, fp)
    if data:
        data_path = os.path.join(pkg_path, 'data')
        os.makedirs(data_path, exist_ok=True)
        for fname,fpath in data:
            file_path = os.path.join(data_path, fname)
            print(fpath, file_path)
            shutil.move(fpath,file_path)


@packages.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    Handles package meta/data fields/files
    """
    if 'files' not in session:
        session['files'] = []
    # if 'fields' not in session:
    #     session['fields'] = {}

    # Handle file upload
    upload = UploadForm()
    if upload.validate_on_submit():
        filename = save_file(upload.file.data)
        session['files'] += [filename]

    # Handle form submit
    form = PackageForm()
    if form.validate_on_submit():
        pack_id = submit_package(form.data, files=session['files'])
        del session['files']
        # del session['fields']
        return redirect(url_for('packages.view', id=pack_id))

    if form.errors:
        flash_errors(form)

    return render_template('packages/create.html',
                            upload=upload, form=form,
                            files=session['files'])
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
