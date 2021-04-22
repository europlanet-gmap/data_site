from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileRequired

# from werkzeug.utils import secure_filename

from wtforms import (
    BooleanField,
    DecimalField,
    FormField,
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
    NumberRange,
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



class UploadFile(FlaskForm):
    """
    File 'upload'
    """
    file = FileField('Data')
    submit = SubmitField('Upload')



class PackageForm(FlaskForm):
    """
    Form for package submission
    """
    gmap_id = StringField(
        'Gmap ID',
        validators=[DataRequired()],
        render_kw={'readonly': True},
        id='gmap_id'
    )

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

    map_type = SelectMultipleField(
        'Map type',
        validators=[DataRequired()],
        choices=[
            ('compositional','Compositional'),
            ('morphological','Morphological'),
            ('stratigraphic','Stratigraphic')
        ],
        id='map_type'
    )

    minlat = DecimalField(
        'Latitude min',
        default=-89,
        validators=[DataRequired(),NumberRange(-90,90)],
        places=None)

    maxlat = DecimalField(
        'Latitude max',
        default=89,
        validators=[DataRequired(),NumberRange(-90,90)],
        places=None)

    westlon = DecimalField(
        'Longitude min (west)',
        default=1,
        validators=[DataRequired(),NumberRange(0,360)],
        places=None)

    eastlon = DecimalField(
        'Longitude max (east)',
        default=359,
        validators=[DataRequired(),NumberRange(0,360)],
        places=None)

    crs = StringField('CRS')
    output_scale = StringField()
    authors = StringField()
    source_data = StringField()
    standards = StringField()
    doi = StringField()
    references = StringField()
    aims = StringField()
    description = StringField()
    related_products = StringField()
    units_definition = StringField()
    stratigraphic_info = StringField()
    comments = StringField()
    heritage = StringField()
    acknowlegments = StringField()

    submit = SubmitField('Submit')
