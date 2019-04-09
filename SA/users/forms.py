from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email

from SA.models import User


#Flask forms for key pages.

class Form_Register(FlaskForm):
    username = StringField('Username', validators = [Length(min=5, max=20), DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])

    submit = SubmitField('Register Account')

class Form_Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    rememberme = BooleanField('Remember me? - Tick this to stay logged in!')

    submit = SubmitField('Login!')


class Form_Update_Account(FlaskForm):
    username = StringField('Username', validators = [Length(min=5, max=20), DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    avatar = FileField('Update Avatar', validators=[FileAllowed(["png","jpg"])])

    submit = SubmitField('Update Account')

class Form_Password_Request(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Request Password Reset')


class Form_Reset_Password(FlaskForm):
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])

    submit = SubmitField('Reset Password')
