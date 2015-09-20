from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

class SignupForm(Form):
    username = TextField('Username', validators = [DataRequired()])
    email = TextField('Email Address', validators = [
        DataRequired(),
        Email()])
    password = PasswordField('Password', validators = [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', validators = [DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class LoginForm(Form):
    username = TextField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
