import os
import simplejson as json

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

from data_site import db, form, utils
from data_site.auth import login_required
from data_site.forms import PackageForm, UploadFile
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


# import shutil
# def save_package(meta, data):
#     base_path = current_app.config['UPLOAD_FOLDER']
#     pkg_path = os.path.join(base_path, meta['gmap_id'])
#     pkg_meta = os.path.join(pkg_path, 'meta.json')
#     with open(pkg_meta, 'w') as fp:
#         json.dump(meta, fp)
#     if data:
#         data_path = os.path.join(pkg_path, 'data')
#         os.makedirs(data_path, exist_ok=True)
#         for fname,fpath in data:
#             file_path = os.path.join(data_path, fname)
#             print(fpath, file_path)
#             shutil.move(fpath,file_path)


class PackageData:
    def __init__(self, meta, data):
        self.meta = meta
        self.data = data
        self.base_path = current_app.config['UPLOAD_FOLDER']

    def commit(self):
        # Write meta/data to disk
        pkg_path = os.path.join(self.base_path, self.meta['gmap_id'].lower())
        os.makedirs(pkg_path, exist_ok=True)
        self._write_meta(under=pkg_path)
        self._write_data(under=pkg_path)

        # Write metadata as readme/markdown to database
        p = DataPackage(name=self.meta['name'], creator_id=current_user.id,
                        planetary_body=self.meta['target_body'],
                        body=json.dumps(self.meta)
                        )
        db.session.add(p)
        db.session.commit()
        return p.id

    def _write_meta(self,under):
        assert self.meta, "Package fields/metadata is not (yet) defined"
        pkg_file = os.path.join(under, 'meta.json')
        with open(pkg_file, 'w') as fp:
            json.dump(self.meta, fp)

    def _write_data(self,under):
        if self.data:
            assert 'dir' in self.data
            assert 'files' in self.data
            temp_dir = self.data['dir']
            dest_dir = os.path.join(under, 'data')
            for fname in self.data['files']:
                temppath = os.path.join(temp_dir, fname)
                destpath = os.path.join(dest_dir, fname)
                shutil.move(temppath, destpath)

    def __del__(self):
        shutil.rmtree(self.data['dir'])


def mkdtemp():
    """
    Return path to temporary dir
    """
    from tempfile import mkdtemp
    tmpdir = utils.Tempdir(dir = current_app.config['UPLOAD_FOLDER'])
    os.makedirs(tmpdir)
    return tmpdir


def save_file(file_form, dir):
    """
    Return filename uploaded
    """
    filename = secure_filename(file_form.filename)
    filepath = os.path.join(dir, filename)
    file_form.save(filepath)
    return filename


@packages.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    Handles package meta/data fields/files
    """
    upload = UploadFile()
    form = PackageForm()

    if 'data' not in session:
        session['data'] = {}

    # Handle file upload
    if upload.validate_on_submit():
        if upload.file.data:
            if 'files' not in session['data']:
                session['data'].update({'dir':mkdtemp(), 'files':[]})
            filename = save_file(upload.file.data, dir=session['data']['dir'])
            session['data']['files'].append(filename)

    # Handle form submit
    if form.validate_on_submit():
        # Clean out wtform related fields from data of interest
        meta = {k:v for k,v in form.data.items()
                    if k not in ('submit','csrf_token')}
        # If data files were uploaded, use them
        data = session['data'] if 'data' in session else None
        # Initialize a "package" object to handle the writing (filesystem & database)
        pkg = PackageData(meta=meta, data=data)
        pack_id = pkg.commit()
        del pkg, session['data']
        # Assuming everything is good, redirect user to new package's view
        return redirect(url_for('packages.view', id=pack_id))

    if form.errors:
        flash_errors(form)

    return render_template('packages/create.html',
                            upload=upload, form=form,
                            files=session['data']['files']
                            )


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
