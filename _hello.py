from flask import render_template

def show(name=None):
    return render_template('hello.html', name=name)
