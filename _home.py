from flask import render_template

def show(name=None):
    # return f'Home page, {name if name else "fulano"}'
    return render_template('home.html', name=name)
