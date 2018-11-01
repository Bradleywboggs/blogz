
#THE LOST BEE
# a 'Bee' in this application refers to something akin to the old practice 
# of  'Quilting Bees' when people from the community would 
# gather to work on quilt together.In this application, we're translating 
# this idea into a similar concept where a digital community
# can gather and work on their own individual crafty projects, 
# but they can do so together, sharing ideas, tips, resources, etc.
#  The site will have as its crux the 'BEE' space, 
# consisting of a page to view and join open bees, view past bees, and start a new bee.
# The site will also have a standard Blog space for Website's curator,
# and possibly other users as the curator gives permissions.
# Finally, the site will have an online store for the website curator's wares 
# served likely by a third party for security reasons.

#TODO: Add Bootstrap! 

from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True   
db = SQLAlchemy(app)
app.secret_key = "*/afdhjajHHDJJ+daa"
#TODO: Change to MVC structure.

#TODO: Add 'Bee' class --- 
#class Bee(db.Model):
#id = db.Column(db.Integer, primary_key=True)
#media = db.Column(db.String(120))  
#creator_id = db.Column(db.Integer, db.ForeignKey('user.id')), 
# length = db.Column(db.Integer) (how long it will go for) etc...

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.author = author
#TODO: Add profile_pic, email, expertise, interests, blog_permissions fields.
class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

#TODO: provide limited access only routes for 'new post', and 'new bee' routes. 
# i.e. instead of allowed_routes have restricted_routes,  
# if request.endpoint in restricted_routes...
#TODO: create  routes for active bees, past bees, create a bee.
@app.before_request
def require_login():
    allowed_routes = ['get_login', 'post_login', 'get_signup', 'post_signup']  
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
 #TODO: Add user account page.
 
@app.route('/login')
def get_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def post_login():
    username = request.form.get('username')
    password = request.form.get('pw')
    user = User.query.filter_by(username=username).first()

    if user and check_pw_hash(password, user.pw_hash) == True:
        session['username'] = username
        flash("Login Successful!")
        return redirect('/')
    else:
        flash("Invalid username or password")
        return redirect('/login')
    
@app.route('/signup')
def get_signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def post_signup():
    username = request.form['username']
    password = request.form['pw']
    verifypw = request.form['verifypw']
    existing_user = User.query.filter_by(username=username).first()

    username_error = ''
    password_error = ''
    verifypw_error = ''
    duplicate_user_error = ''
    # # Regex pattern checks for non-white space characters - minimum 4, maximum 20
    username_pattern = re.compile(r'[^\s]{4,20}')
    username_matched = username_pattern.match(username)
    # Regex pattern checks for non-white space characters - minimum 4, maximum 20
    pw_pattern = re.compile(r'[^\s]{4,20}')
    pw_matched = pw_pattern.match(password)
    
    #verify username
    if not username_matched:
        username_error =  'error'
        flash('This username is not valid', 'error')
    else:
        username = username
        if existing_user:
            duplicate_user_error = 'error'
            flash('User already exists.', 'error')
        else:

    # validate password
            if password == '':
                password_error = 'error'
                flash('Please enter a password', 'error')
                password = ''
                verifypw = ''      
            elif not pw_matched:
                password_error = 'error'
                flash('This password is not valid', 'error')
                password = ''
                verifypw = ''    
        # verify both passwords match
            elif password != verifypw:
                verifypw_error = 'error'
                flash('Passwords do not match.', 'error')
                password = ''
                verifypw = ''
            else:
                password = password
                verifypw = verifypw   

    if not username_error and not password_error and not verifypw_error and not duplicate_user_error:
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        flash('Signup successful!', category='success')
        return redirect('/')
    #TODO: Determine if re-rendering template is needed. 
    else:
        return render_template('signup.html', 
        password_error=password_error, username_error=username_error, verifypw_error=verifypw_error,duplicate_user_error=duplicate_user_error,
        password='', verifypw='', username=username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/')
@app.route('/index')
def index():
    if not request.args:
        authors = User.query
        return render_template('index.html', authors=authors)
    else:
        author_id = int(request.args.get('id'))
        user = User.query.get(author_id)
        posts = Post.query.filter_by(author_id=author_id).all()
        return render_template('displayposts.html', posts=posts, user=user)

#TODO: Add delete, edit functionality for posts, if logged-in user is author of original post
@app.route('/blog')
def get_blogs():
    if not request.args:
        posts = Post.query.order_by(desc(Post.pub_date)).all()
        return render_template('allblogs.html', posts=posts)
    else:
        post_id = int(request.args.get('id'))
        post = Post.query.get(post_id)
        return render_template('displaypost.html',post=post)
@app.route('/blog', methods=['POST'])
def post_blogs():
    title = request.form['title']
    body = request.form['body']
    post_id = request.form['id']
    pub_date = Post.query.filter_by
    author = User.query.filter_by(username=session['username']).first()

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
        
        new_post = Post(title, body, author)
        db.session.add(new_post)
        db.session.commit()
        return render_template('displaypost.html',post = new_post)

@app.route('/newpost')
def add_post():
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()