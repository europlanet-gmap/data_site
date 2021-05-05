import click
from flask.cli import with_appcontext


@click.command('import-planmap')
@with_appcontext
def import_planmap_packages():
    from .scraper import scrape_maps
    from data_site.models import DataPackage, User
    from data_site.extensions import db
    bodies = scrape_maps()

    user = User.query.filter_by(email="planmap-eu@gmail.com").first()
    if user is None:
        user = User(username="planmap-heritage", email="planmap-eu@gmail.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()

    for body in bodies:
        for map in body.maps:
            from data_site.models import PlanetaryBody
            from sqlalchemy import func
            f = PlanetaryBody.query.filter(func.lower(PlanetaryBody.name) == body.name.lower()).first()
            if f is None:
                f = PlanetaryBody.get_unknwon_body()

            id = f.id

            import markdown
            p = DataPackage(name=map.name, creator_id=user.id,
                            planetary_body_id=id, description=markdown.markdown(map.readme, extensions=["tables"]),
                            thumbnail_url=map.thumb_url)
            db.session.add(p)

    db.session.commit()


@click.command("remove-planmap")
@with_appcontext
def remove_planmap_entries():
    from ..models import User
    from data_site.extensions import db

    packs = User.query.filter_by(email="planmap-eu@gmail.com").first().packages
    for p in packs:
        db.session.delete(p)
        db.session.commit()
