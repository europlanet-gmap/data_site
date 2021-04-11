import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    current_app
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from data_site.auth import login_required
from data_site.db import get_db
from data_site import form


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
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
                form_ok = form.validate(form_parsed, errors)
            except Exception as err:
                raise err
            else:
                values['metadata'] = form_parsed
            if not form_ok:
                assert errors, errors
                [ flash(e) for e in errors ]
            else:
                flash('success')
                db = get_db()
                db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
                return redirect(url_for('blog.index'))
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


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
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
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
