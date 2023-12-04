"""
    Forms
    ~~~~~
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, Form
from wtforms import BooleanField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import EqualTo
from wtforms.validators import ValidationError

from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users

from flask_wtf import FlaskForm
from wtforms import FileField
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField, HiddenField


class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[FileRequired()])


class URLForm(FlaskForm):
    url = StringField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(FlaskForm):
    term = StringField('', [InputRequired()])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(FlaskForm):
    title = StringField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = StringField('')
    file = FileField('File')
    imageData = HiddenField('ImageData')


class LoginForm(FlaskForm):
    name = StringField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    def validate_name(form, field):
        user = current_users.get_user(field.data)
        if not user:
            raise ValidationError('This username does not exist.')

    def validate_password(form, field):
        user = current_users.get_user(form.name.data)
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError('Username and password do not match.')


class ChangePasswordForm(LoginForm):
    new_password = PasswordField('', [InputRequired()])

    def validate_new_password(self, field):
        # Add any additional validation for the new password if needed
        pass


class RegistrationForm(FlaskForm):
    username = StringField('', validators=[InputRequired()])
    password = PasswordField('', validators=[InputRequired()])
    confirm_password = PasswordField('', validators=[InputRequired(), EqualTo('password')])

    def validate_username(self, field):
        user = current_users.get_user(field.data)
        if user:
            raise ValidationError('This username is already taken. Please choose a different one.')