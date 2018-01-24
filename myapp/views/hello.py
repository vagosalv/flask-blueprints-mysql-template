from flask import Blueprint,render_template

from ..app import mysql


hello = Blueprint('hello',__name__)

#arxikh
@hello.route('/')
def index_page():
	return render_template('home.html')

#About
@hello.route('/p13alva/about')
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




