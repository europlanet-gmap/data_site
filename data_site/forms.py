from flask_wtf import FlaskForm

from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    ValidationError
    )

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp
    )

from .models import User



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    # name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(1, 20),
            Regexp('^[a-zA-Z0-9]*$',
                    message='The username should contain only a-z, A-Z and 0-9.')
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(), Length(1, 254), Email()
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(), Length(8, 128), EqualTo('password2')
        ]
    )

    password2 = PasswordField(
        'Confirm password',
        validators=[DataRequired()]
    )

    submit = SubmitField()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class PackageForm(FlaskForm):
    """
    Form for package submission
    """
    name = StringField(
        'Name',
        validators=[DataRequired()],
        id='name'
    )

    target_body = SelectField(
        'Target body',
        validators=[DataRequired()],
        choices=[
            'Mars',
            'Mercury',
            'Moon'
        ],
        id='target_body'
    )

    gmap_id = StringField(
        'Gmap ID',
        validators=[DataRequired()]
    )

    map_type = SelectMultipleField(
        'Map type',
        validators=[DataRequired()],
        choices=[
            ('compositional','Compositional'),
            ('morpho','Morpho'),
            ('stratigraphic','Stratigraphic')
        ],
        id='map_type'
    )

    submit = SubmitField()
