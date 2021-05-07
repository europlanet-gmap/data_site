from loginpass import create_gitlab_backend

Gitlab = create_gitlab_backend("gitlab", "git.europlanet-gmap.eu")


def normalize_userinfo(client, data):
    return {
        'sub': str(data['id']),
        'name': data['name'],
        'email': data.get('email'),
        'preferred_username': data['username'],
        'profile': data['web_url'],
        'picture': data['avatar_url'],
        'website': data.get('website_url'),
        'is_admin': data.get("is_admin"),
        'gitlab_page' : data.get("profile"),
        'twitter': data.get("twitter"),
        "data": data
    }

Gitlab.OAUTH_CONFIG["userinfo_compliance_fix"] = normalize_userinfo
Gitlab.OAUTH_CONFIG["client_kwargs"]= {
        'scope': 'read_user api'
    }
backends = [Gitlab]


def register_blueprints(app):
    from loginpass import create_flask_blueprint

    from data_site.main import main
    from data_site.auth import auth
    from data_site.packages import packages
    from data_site.extensions import oauth
    from .auth import handle_authorize


    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(packages, url_prefix='/')
    app.add_url_rule('/', endpoint='index')

    bp = create_flask_blueprint(backends, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='')

