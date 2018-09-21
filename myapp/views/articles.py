from flask import Blueprint, Flask, render_template, flash, url_for, session, request, logging, redirect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mysqldb import MySQL
from ..app import mysql
from .users import is_logged_in
#twra to evala
from .comments import *

art = Blueprint('art',__name__, template_folder='templates')


class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=10)])


#Articles
@art.route('/articles')
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
@art.route('/test/<string:id>/')
def test(id):
	#Create cursor
	c = mysql.db.cursor()
	#Get Article
	result = c.execute("SELECT * FROM comments WHERE article_id = %s", [id])
	if result > 0 :
		result = c.execute("SELECT articles.* , comments.* FROM articles, comments WHERE articles.id = %s and comments.article_id = articles.id ",[id])
	else:
		result = c.execute("SELECT * FROM articles WHERE id = %s", [id])	

	#Commit
	article = c.fetchone()
	return render_template('test.html', article=article)

# Gia otan anoigw to article na emfanizei to swsto periexomeno
@art.route('/article/<string:id>/')
def article(id):
    #Create cursor
	c = mysql.db.cursor()
	#Get Article
	result = c.execute("SELECT * FROM comments WHERE article_id = %s", [id])
	if result > 0 :
		result = c.execute("SELECT articles.* , comments.* FROM articles, comments WHERE articles.id = %s and comments.article_id = articles.id ",[id])
	else:
		result = c.execute("SELECT * FROM articles WHERE id = %s", [id])	

	#Commit
	article = c.fetchone()
	return render_template('article.html', article=article)
	
	
#gia otan anoigw to article na emfanizontai ta swsta comments
@art.route('/comment/<string:id>/')
def comment(id):
    #Create cursor
    c = mysql.db.cursor()
    #Get Comment
    while result is not None:
    	result = c.execute("SELECT * FROM comments WHERE id = %s", [id])
    	comment = c.fetchone()
	
    return render_template('comment.html', comment=comment)	

	
	#Add article
@art.route('/add_article', methods=['GET', 'POST'])
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
@art.route('/edit_article/<string:id>', methods=['GET', 'POST'])
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
@art.route('/delete_article/<string:id>', methods=['POST'])
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
