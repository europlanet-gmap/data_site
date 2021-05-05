from flask import Blueprint, render_template, redirect

main = Blueprint('main', __name__)
from . import menu_manager

@main.route('/')
def index():
    from .models import DataPackage
    packages = DataPackage.query.filter(DataPackage.thumbnail_url != "").order_by('creation_date').limit(9)

    return render_template('main/index.html', packages=packages, spanning=4)
