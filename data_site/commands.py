
from flask.cli import with_appcontext
import click

def init_commands(app):
    app.cli.add_command(update_planetary_bodies_list)
    app.cli.add_command(initialize)

def create_default_entries():
    from .models import PlanetaryBody
    from . import db
    default = PlanetaryBody(name="Unknown", is_planet=False)
    print(f"def instantiated {default}")
    print(db.session.add(default))
    print("added")

    print("going to commit")
    print(db.session.commit())

    print("Def entry created")

    print('---> FIRST RUN: Created Database!')


@click.command('update_bodies', help="initialize the db with a list of planetary bodies")
@click.option('-f', '--force',  is_flag=True, help="Force overwrite already existing records")
@with_appcontext
def update_planetary_bodies_list(force=False):

    from .models import PlanetaryBody
    from . import db

    if force:
        print("OVERWRITING entries")

    def add_body_if_missing(name, is_planet=False):
        if name == "":
            return
        if isinstance(is_planet, str):
            is_planet = True if is_planet.lower().strip() == 'true' else False
        name = name.strip()
        found = PlanetaryBody.query.filter_by(name=name).first()
        if not found:
            print(f"adding {name}")
            default = PlanetaryBody(name=name, is_planet=is_planet)
            db.session.add(default)
            db.session.commit()

        else: # already present
            if force:
                db.session.delete(found)
                db.session.commit()
                add_body_if_missing(name, is_planet)


    import pandas
    bodies = pandas.read_csv("instance/default_bodies.txt").values

    for b, is_planet in bodies:
        add_body_if_missing(b, is_planet.strip())

    import requests, json

    a = requests.get("https://api.le-systeme-solaire.net/rest/bodies")
    try:
        bodies = json.loads(a.content)["bodies"]
    except:
        print("cannot create entries, probably malformed request content")
        return

    for b in bodies: # there are much more data in this db, in the future we could support it
        name = b['englishName']
        is_planet = b['isPlanet']

        if name == "":
            continue

        add_body_if_missing(name, is_planet)

@click.command('first_init', help="initialize the app with def entries (for dev testing)")
@with_appcontext
@click.pass_context
def initialize(ctx):
    print("init")
    from .auth import init_roles

    ctx.invoke(init_roles)

    ctx.invoke(update_planetary_bodies_list)
    from .planmap_importer import import_planmap_packages
    ctx.invoke(import_planmap_packages)
    #
    from .models import Role
    Role.init_default_roles()
