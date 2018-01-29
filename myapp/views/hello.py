from flask import Blueprint, Flask, render_template, flash, url_for, session, request, logging, redirect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
#prepei na mpei?
from flask_mysqldb import MySQL

from ..app import mysql


hello = Blueprint('hello',__name__)



# Gia otan anoigw to article na emfanizei to swsto periexomeno
@hello.route('/test/<string:id>/')
def test(id):
	#Create cursor
	c = mysql.db.cursor()
	#Get Article
	result = c.execute("SELECT * FROM articles WHERE id = %s", [id])
	if result > 0 :
		result = c.execute("SELECT articles.* , comments.* FROM articles, comments WHERE articles.id = %s and comments.article_id = articles.id ",[id])
	else:
		result = c.execute("SELECT * FROM articles WHERE id = %s", [id])	

	#Commit
	article = c.fetchone()
return render_template('test.html', article=article)


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

#Edit article
@hello.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #create cursor
    c = mysql.db.cursor()
    #get article by id
    result = c.execute("SELECT * FROM articles WHERE id = %s",[id])
    article = c.fetchone()
    #Get form
    form = ArticleForm(request.form)
    #populate article form fields
    form.title.data = article[1]
    form.body.data = article[3]

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        #Create cursor
        c = mysql.db.cursor()
        #execute
        c.execute("UPDATE articles SET title=%s, body=%s WHERE id =%s",(title, body, id))
        #commit
        mysql.db.commit()
        #close connection
        c.close()
        flash('Article Updated', 'success')
        return redirect(url_for('hello.dashboard'))

    return render_template('edit_article.html', form=form)


#Delete article
@hello.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    #create cursor
    c = mysql.db.cursor()
    #execute
    c.execute("DELETE FROM articles WHERE id = %s", [id])
    #commit
    mysql.db.commit()
    #close connection
    c.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('hello.dashboard'))

#Commnts Form class
class CommentForm(Form):
    body = TextAreaField('Body', [validators.Length(min=10)])

#Comments
@hello.route('/comments')
def comments():
    #Create cursor
    c = mysql.db.cursor()
    #Get Articles
    result = c.execute("SELECT * FROM comments")
    comments = c.fetchall()
    if result > 0 :
        return render_template('comments.html', comments=comments)
    else:
        msg = 'No comments Found'
        return render_template('comments.html', msg=msg)
    #close connection
    c.close()

#gia otan anoigw to article na emfanizontai ta swsta comments
@hello.route('/comment/<string:id>/')
def comment(id):
    #Create cursor
    c = mysql.db.cursor()
    #Get Comment
    result = c.execute("SELECT * FROM comments WHERE id = %s", [id])
    comment = c.fetchone()
    return render_template('comment.html', comment=comment)


#Add comment
@hello.route('/add_comments/<string:article_id>', methods=['GET', 'POST'])
@is_logged_in
def add_comment(article_id):

    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        body = form.body.data
        #Create cursor
        c = mysql.db.cursor()
        #execute
        c.execute("INSERT INTO comments(author, body, article_id) VALUES(%s, %s, %s)", (session['username'], body, [article_id]))
        #commit
        mysql.db.commit()
        #close connection
        c.close()
        flash('Comment created', 'success')
        return redirect(url_for('hello.dashboard'))

    return render_template('add_comments.html', form=form)


#Edit comment
@hello.route('/edit_comment/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_comment(id):
    #create cursor
    c = mysql.db.cursor()
    #get comment by id
    result = c.execute("SELECT * FROM comments WHERE id = %s",[id])
    comment = c.fetchone()
    #Get form
    form = CommentForm(request.form)
    #populate comment form fields
    form.body.data = comment['body']

    if request.method == 'POST' and form.validate():
        body = request.form['body']
        #Create cursor
        c = mysql.db.cursor()
        #execute
        c.execute("UPDATE comments SET  body=%s WHERE id =%s",( body, id))
        #commit
        mysql.db.commit()
        #close connection
        c.close()
        flash('Comment Updated', 'success')
        return redirect(url_for('hello.dashboard'))

    return render_template('edit_comment.html', form=form)

#Delete article
@hello.route('/delete_comment/<string:id>', methods=['POST'])
@is_logged_in
def delete_comment(id):
    #create cursor
    c = mysql.db.cursor()
    #execute
    c.execute("DELETE FROM comments WHERE id = %s", [id])
    #commit
    mysql.db.commit()
    #close connection
    c.close()
    flash('Comment Deleted', 'success')
    return redirect(url_for('hello.dashboard'))

