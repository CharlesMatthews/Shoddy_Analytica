from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
from SA.models import User



class RegisterForm(FlaskForm):
    username = StringField('Username', validators = [Length(min=5, max=20), DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])

    submit = SubmitField('Register Account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    rememberme = BooleanField('Remember me? - Tick this to stay logged in!')

    submit = SubmitField('Login!')


"""
class RegisterForm(FlaskForm):
    username = StringField('Username', validators = [Length(min=5, max=20), DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired(), Length(min=8)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])

    submit = SubmitField('Register Account')

"""
