import click
# from flask import current_app, g
from flask.cli import with_appcontext



# from .. import db


@click.command('import-planmap')
@with_appcontext
def import_planmap_packages():
    from .scraper import scrape_maps
    from ..models import DataPackage, User
    from .. import db
    bodies = scrape_maps()
    # print(maps)

    user = User.query.filter_by(email="planmap-eu@gmail.com").first()
    if user is None:
        user = User(username="planmap-heritage", email="planmap-eu@gmail.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()




    for body in bodies:
        for map in body.maps:
            print(map.name)


            p = DataPackage(name=map.name, creator_id=user.id)
            db.session.add(p)
            db.session.commit()


@click.command("remove-planmap")
@with_appcontext
def remove_planmap_entries():

    from ..models import DataPackage, User
    from .. import db

    packs = User.query.filter_by(email="planmap-eu@gmail.com").first().packages
    for p in packs:
        db.session.delete(p)
        db.session.commit()


