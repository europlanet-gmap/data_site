from .importer import import_planmap_packages, remove_planmap_entries


def init_app(app):
    print("adding import-planmap command")
    app.cli.add_command(import_planmap_packages)
    app.cli.add_command(remove_planmap_entries)