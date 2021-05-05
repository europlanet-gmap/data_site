# GMAP data submission

This repository host the code for the data-submission website.
It provides an interface form-based to check and submit a data and metadata sets
composing a GMAP data package.

Is is built with Python Flask, and provides a form based on a Meta JSON file.
The backend being Python eases the integration between frontend and the backend
tools we already have built.


## Run help
To see the available commands to run flask (locally):

```bash
$ flask
```


### Initialize App roles
User roles (admin, etc) need to be initialized:

```bash
$ flask auth init_roles
```


### Planmap sample data
To start the app with sample/example data, do

```bash
$ flask first_init
```


## Develper notes

```bash
$ export FLASK_APP='data_site'
$ export FLASK_ENV='development'
$
$ flask run
```

> And then, `$ flask run```


## Important notes
- we now use bootstrap-flask for managing bootstrap (this changes the templates also)
- to handle changes in the structure of the DB we now use [migrate](https://github.com/miguelgrinberg/Flask-Migrate). If the models were changed we need to:

```bash
$ flask db init [first time user]
$ flask db migrate
$ flask db upgrade
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
- A dummy password is set for the planmap-heritage user


# TODO

- [ ] Make a frontpage (index) with a minimal form (eg, "{ name: <> }")
- [ ] Use Flask-email to send out emails


# modules to consider
- https://potion.readthedocs.io to manage the Restful API
