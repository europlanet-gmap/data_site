from flask import Blueprint, render_template, request, flash, redirect, url_for

from .forms import RegisterForm, LoginForm
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

auth = Blueprint('auth', __name__)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='/', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('Login success.', 'info')
                return redirect_back()
            else:
                flash('Your account is blocked.', 'warning')
                return redirect(url_for('/'))
        flash('Invalid email or password.', 'warning')
    return render_template('auth/login.html', form=form)
#
# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#
#         user = User.query.filter_by(email=email).first()
#         if user:
#             if check_password_hash(user.password, password):
#                 flash('Logged in successfully!', category='success')
#                 login_user(user, remember=True)
#                 return redirect(url_for('views.home'))
#             else:
#                 flash('Incorrect password, try again.', category='error')
#         else:
#             flash('Email does not exist.', category='error')
#
#     return render_template("auth/login.html", user=current_user)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('blog.index'))


# @auth.route('/register', methods=['GET', 'POST'])
# def sign_up():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstName')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')
#
#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash('Email already exists.', category='error')
#         elif len(email) < 4:
#             flash('Email must be greater than 3 characters.', category='error')
#         elif len(first_name) < 2:
#             flash('First name must be greater than 1 character.', category='error')
#         elif password1 != password2:
#             flash('Passwords don\'t match.', category='error')
#         elif len(password1) < 7:
#             flash('Password must be at least 7 characters.', category='error')
#         else:
#             new_user = User(email=email, first_name=first_name, password_hash=generate_password_hash(
#                 password1, method='sha256'))
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user, remember=True)
#             flash('Account created!', category='success')
#             return redirect(url_for('views.home'))
#
#     return render_template("auth/register.html", user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # token = generate_token(user=user, operation='confirm')
        # send_confirm_email(user=user, token=token)
        # flash('Confirm email sent, check your inbox.', 'info')
        flash('Registration successfull.', 'info')
        return redirect(url_for('.login'))


    return render_template('auth/register.html', form=form)