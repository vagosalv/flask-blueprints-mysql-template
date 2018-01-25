from flask import Blueprint,render_template

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



