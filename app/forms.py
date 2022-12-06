
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
#REGISTRATION##
class RegistrationForm(FlaskForm):
    #username = StringField('Username', 
    #validators = [DataRequired(), Length(min = 2, max = 20)])

    ## create email part of registration
    email = StringField('Email', validators = [DataRequired(),Email()])

    #password registration
    password = PasswordField('Password', validators = [DataRequired(),Length(min = 2, max = 60)])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')

    #Function within form that prevents duplicate emails
    def validate_email(self,email):
        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('An account with that email already exists.')
##END OF REGISTRATION 
class LoginForm(FlaskForm):
    
    ## create email part of registration
    email = StringField('Email', validators = [DataRequired(), Email()])

    #password registration
    password = PasswordField('Password', validators = [DataRequired(),Length(min = 2, max = 60)])
    
    submit = SubmitField('Login')
#form to update tracks
class PostForm(FlaskForm):
    track = TextAreaField('New Track Information:', validators = [DataRequired()])
    album = TextAreaField('New Album Information:', validators = [DataRequired()])
    submit = SubmitField('Update')
#form to update artists
class UpdateArtistForm(FlaskForm):
    artist = TextAreaField('New Artist Information:', validators = [DataRequired()])
    genre = TextAreaField('New Genre Information:', validators = [DataRequired()])
    submit = SubmitField('Update')
#form to update users
class UpdateUserForm(FlaskForm):
    email = TextAreaField('Updated User Email:', validators = [DataRequired()])
    password = TextAreaField('Updated Password:', validators = [DataRequired()])
    submit = SubmitField('Update')
#form to add users
class AddUserForm(FlaskForm):
    email = TextAreaField('New User Email:', validators = [DataRequired()])
    password = TextAreaField('New User Password:', validators = [DataRequired()])
    submit = SubmitField('Add')