from flask import url_for, session, jsonify, render_template
from flask_login import current_user, login_required
from werkzeug.utils import redirect


def register_dev_routes(app):
    @app.route("/send")
    def send_test_email():
        from .emails import send_mail
        body = '''
    # test
    
    
    this is a test message
    
    testing the email send
            '''
        m = send_mail("luca.penasa@gmail.com", subject="test message", body=body, body_is_markdown=True,
                      to_user=current_user)
        return m

    @app.route("/newpack")
    def newpack():
        return redirect(url_for("user_packs.create_view"))

        # http: // localhost: 5000 / admin / user_packs / new /


    @app.route("/gitlab")
    @login_required
    def gitlab():
        token = session.get("gitlab_token", None)
        if token is None:
            return render_template("gitlab/gitlab.html", data={})

        import gitlab
        gl = gitlab.Gitlab(app.config["GITLAB_URL"], oauth_token=token["access_token"])

        projects = gl.projects.list()

        out = {}
        for p in projects:
            out[p.id] = {"project_name" : p.name}
            issues = p.issues.list()
            iss = {}
            for i in issues:
                iss[i.id] = dict(title=i.title)
            out[p.id]["issues"] = iss


        return render_template("gitlab/gitlab.html", data=out)


