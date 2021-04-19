from flask import Blueprint, flash, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    flash("Home page. to be done")
    return render_template('main/index.html')