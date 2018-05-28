from flask import Blueprint, Flask, render_template, flash, url_for, session, request, logging, redirect
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_mysqldb import MySQL
from ..app import mysql
from .users import is_logged_in


com = Blueprint('com',__name__, template_folder='templates')

#Commnts Form class
class CommentForm(Form):
    body = TextAreaField('Body', [validators.Length(min=10)])

#Comments
@com.route('/comments')
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




#Add comment
@com.route('/add_comments/<string:article_id>', methods=['GET', 'POST'])
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
@com.route('/edit_comment/<string:id>', methods=['GET', 'POST'])
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

#Delete comment
@com.route('/delete_comment/<string:id>', methods=['POST'])
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
