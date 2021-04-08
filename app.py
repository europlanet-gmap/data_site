import os
import json

from flask import Flask
from flask import request
from flask import redirect, url_for
from flask import session, escape
from flask import render_template

import _home
import _hello
import _submit


# # Load the (default) schema
# #
# _curdir = os.path.dirname(os.path.abspath(__file__))
# with open(os.path.join(_curdir, 'form.schema.json'), 'r') as fp:
#     FORM_SCHEMA = json.load(fp)
# del _curdir
from form_schema import schema as FORM_SCHEMA

_submit.register_schema(FORM_SCHEMA)

app = Flask(__name__)

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
def submit():
    if request.method == 'POST':
        error = None
        try:
            form_parsed = _submit.parse_form(request.form)
            form_ok = _submit.validate_form(form_parsed)
        except Exception as err:
            raise err

        if form_ok:
            try:
                # If "do-submit" succeeds, out is some green html page
                out = _submit.do_submit(form_parsed)
                return out
            except Exception as err:
                error = str(err)
        else:
            error = 'Invalid fields'
        return _submit.show_form(error=error, values=form_parsed)
    return _submit.show_form()


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        out = _upload.do_upload(request.files)
        return out


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
