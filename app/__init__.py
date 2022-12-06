##Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#import spotipy
import os
#import requests

###BEGINNING OF SPOTITFY ADDING STUFF

#currently in spotify.py - hopefully is easier to keep track of

##END OF ADDING STUFF TO SPOTIFY

#__name__ refers to local python file
app = Flask(__name__)
#Create secret key for website
app.config['SECRET_KEY'] = '4de316f46ad6af0ed9a5fa972606f225'

##DATABASE CONTROLS

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view ='login'
from app import routes