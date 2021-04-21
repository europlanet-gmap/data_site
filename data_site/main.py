from flask import Blueprint, flash, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    from .models import DataPackage
    packages = DataPackage.query.filter(DataPackage.thumbnail_url != "").order_by('creation_date').limit(9)
    # User.name.isnot(None)
    return render_template('main/index.html', packages=packages, spanning=4)