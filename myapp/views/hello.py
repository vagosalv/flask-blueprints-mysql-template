from flask import Blueprint, Flask, render_template, flash, url_for, session, request, logging, redirect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
#prepei na mpei?
from flask_mysqldb import MySQL

from ..app import mysql



hello = Blueprint('hello',__name__)


from .users import *

from .articles import *

from .comments import *


#arxikh
@hello.route('/')
def index_page():
	return render_template('home.html')

#About
@hello.route('/about')
def about():
    return render_template('about.html')

#Dashboard
@hello.route('/dashboard')
@is_logged_in
def dashboard():
    #Create cursor
    c = mysql.db.cursor()
    #Get Articles
    result = c.execute("SELECT * FROM articles")
    articles = c.fetchall()
    if result > 0 :
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No articles Found'
        return render_template('dashboard.html', msg=msg)
    #close connection
    c.close()




