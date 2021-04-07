from flask import Flask
from flask import request

import _submit

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        return _submit.do_submit()
    else:
        return _submit.show_form()
