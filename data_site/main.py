from flask import Blueprint, render_template, redirect, current_app

main = Blueprint('main', __name__)

@main.route('/')
def index():
    from .models import DataPackage
    q = DataPackage.query.filter(DataPackage.thumbnail_url != "")
    packages = q.order_by('creation_date').limit(current_app.config['MAIN_PAGE_LAST_ITEMS_NUMBER'])
    return render_template('main/index.html', packages=packages, spanning=4)
