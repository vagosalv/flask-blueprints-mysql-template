from flask import Blueprint, Flask, render_template, flash, url_for, session, request, logging, redirect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
#prepei na mpei?
from flask_mysqldb import MySQL

from ..app import mysql


hello = Blueprint('hello',__name__)

#arxikh
@hello.route('/')
def index_page():
	return render_template('home.html')

#About
@hello.route('/about')
def about():
    return render_template('about.html')


#Articles
@hello.route('/articles')
def articles():
    #Create cursor
    c = mysql.db.cursor()
    #Get Articles
    result = c.execute("SELECT * FROM articles")
    articles = c.fetchall()
    if result > 0 :
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No articles Found'
        return render_template('articles.html', msg=msg)
    #close connection
    c.close()


# Gia otan anoigw to article na emfanizei to swsto periexomeno
@hello.route('/article/<string:id>/')
def article(id):
    #Create cursor
    c = mysql.db.cursor()
    #Get Article
    result = c.execute("SELECT * FROM articles WHERE id = %s", [id])
    #Commit
    article = c.fetchone()
    def comments(id):
        c = mysql.db.cursor()
        result = c.execute("SELECT * FROM comments WHERE article.id = %s", [article.id])
        comment = c.fetchone()
        return render_template('article.html', comment=comment)
    return render_template('article.html', article=article)


#klash gia elenxo ths formas
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


#User register
@hello.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        c = mysql.db.cursor()

        # Execute query
        c.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.db.commit()

        #Close connection
        c.close()

        flash ('You are now registered and can log in', 'Success')

        redirect(url_for('hello.index_page'))


        return redirect(url_for('hello.login'))
    return render_template('register.html', form = form)


#User login
@hello.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']
        #Create cursor
        c = mysql.db.cursor()
        #Get user by username
        result = c.execute("SELECT * FROM users WHERE username = %s" , [username])

        if result > 0:
            #Get stored hash
            data = c.fetchone()
            password = data[4]#htan 'password'

            #Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('hello.dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error )
            #close connection
            c.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error )


    return render_template('login.html')


#Check if user is logged_in (snippet)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('hello.login'))
    return wrap


#Logout
@hello.route('/logout')
@is_logged_in
def logaout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('hello.login'))


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

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=10)])
	

#Add article
@hello.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        #Create cursor
        c = mysql.db.cursor()
        #execute
        c.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        #commit
        mysql.db.commit()
        #close connection
        c.close()
        flash('Article created', 'success')
        return redirect(url_for('hello.dashboard'))

    return render_template('add_article.html', form=form)

