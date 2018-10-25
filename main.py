from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True   
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, pub_date=None): #author):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        # self.author = author


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120))
    # posts = db.relationship('Post', backref='user')

    def __init__(self, email, password):
        self.email = email
        self.password = password
    

@app.route('/', methods=['POST', 'GET'])
@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        post_id = request.form['id']

        title_error = ''
        body_error = ''

        if not title:
            title_error = "Please enter a title."
            title = ''
        else:
            title = title
            title_error = title_error
    
        if not body:
            body_error = "Please write something here."
            body = ''
        else:
            body = body
            body_error = body_error
        
        if title_error or body_error:
            return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)
        else:    
            new_post = Post(title, body)
            db.session.add(new_post)
            db.session.commit()
            post = Post.query.get(post_id) 
            return render_template('displaypost.html', title=new_post.title, body=new_post.body )
    else:
        if not request.args:
            posts = Post.query.order_by(desc(Post.pub_date)).all()
            return render_template('index.html', posts=posts)
        else:
            post_id = int(request.args.get('id'))
            post = Post.query.get(post_id)
            return render_template('displaypost.html',title=post.title, body=post.body, pub_date=post.pub_date)

@app.route('/newpost')
def add_post():
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()