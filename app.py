import os
import json

from flask import Flask, flash
from flask import request
from flask import redirect, url_for
from flask import session, escape
from flask import render_template

from werkzeug.utils import secure_filename

import _home
import _hello
import _submit

import backend

app = Flask(__name__)


from form_schema import schema as FORM_SCHEMA

# # Load the (default) schema
# #
_curdir = os.path.dirname(os.path.abspath(__file__))
# with open(os.path.join(_curdir, 'form.schema.json'), 'r') as fp:
#     FORM_SCHEMA = json.load(fp)
# del _curdir
_submit.register_schema(FORM_SCHEMA)


UPLOAD_FOLDER = os.path.join(_curdir, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'tif', 'tiff', 'zip', 'gpkg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(16)

@app.route('/')
def index():
    username = session['username'] if 'username' in session else None
    return _home.show(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return _hello.show(name=name)


@app.route('/submit', methods=['GET', 'POST'])
def submit(values={'files':None, 'metadata':None}):
    if request.method == 'POST':
        form_files = None
        form_metadata = None
        error = None
        if '_form_metadata' in request.form:
            _form = request.form.copy()
            _form.pop('_form_metadata')
            try:
                form_parsed = _submit.parse_form(_form)
                form_ok = _submit.validate_form(form_parsed)
            except Exception as err:
                raise err
            else:
                values['metadata'] = form_parsed
            if form_ok:
                try:
                    # If "do-submit" succeeds, out is some green html page
                    out = _submit.do_submit(form_parsed)
                    return out
                except Exception as err:
                    error = str(err)
            else:
                error = 'Invalid fields'
        else:
            assert '_form_upload' in request.form
            # _form = request.form.copy()
            # _form.pop('_form_upload')
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                localpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(localpath)
                try:
                    res = backend.verify_data(localpath)
                except Exception as err:
                    os.remove(localpath)
                    raise err
                else:
                    if res:
                        values['files'] = values['files'] + [filename] if values['files'] else [filename]
                    else:
                        os.remove(localpath)
        # return _submit.show_form(error=error, metadata=values['metadata'], files=values['files'])

    return _submit.show_form(metadata=values['metadata'], files=values['files'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        out = _upload.do_upload(request.files)
        return out


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
