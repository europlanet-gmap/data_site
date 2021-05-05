# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

from flask import current_app, render_template
from flask_mail import Message
from markupsafe import Markup

from . import mail
from markdown import markdown

def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, body, to_user=None, template="emails/message_base.html", body_is_markdown=False):
    if body_is_markdown:
        body = Markup(markdown(body, extensions=["tables"]))

    message = Message(current_app.config['MAIL_PREPEND'] +" "+ subject, recipients=[to])
    rend = render_template(template, user=to_user, message_body=body)
    # message.body = rend
    message.html = rend

    app = current_app._get_current_object()
    # _send_async_mail(app, message)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    # return thr

    return body
