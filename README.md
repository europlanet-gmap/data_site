

# GMAP data submission

This repository host the code for the data-submission website.
It provides an interface form-based to check and submit a set of data packages
and the necessary metadata to compose a GMAP data package.

Is is built with Python Flask, and provides a form based on a Meta JSON file.
The backend being Python eases the integration between frontend and the backend
tools we already have built.


## Important notes
- we now use bootstrap-flask for managing boostrap (this changes the templates also)
- to handle changes in the structure of the DB we now use [migrate](https://github.com/miguelgrinberg/Flask-Migrate). If the models were changed we need to:

```bash
$ flask db init [first time user]
$ flask db migrate
$ flask db upgrade
```

## Run in development mode

```bash
$ flask run
```


## Dirty planmap dataset importer
The importer scrapes data.planmap to import dataset

Example:
```bash
$ flask import-planmap
```

to delete all planmap packages:
```bash
$ flask remove-planmap
```

- A new user "planmap-heritage" is automatically creater the first time
- A dummy pasword is set for the planmap-heritage user




# TODO

- [ ] Make a frontpage (index) with a minimal form (eg, "{ name: <> }")
