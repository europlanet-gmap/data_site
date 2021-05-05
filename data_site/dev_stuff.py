from flask_login import current_user


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