from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True   
db = SQLAlchemy(app)
app.secret_key = "*/afdhjajHHDJJ+daa"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120)) #TODO: MODELS-Change db.String(120) to more reasonable Superclass.
    pub_date = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.author = author

class User(db.Model): #TODO MODELS: Change email to Username
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['get_login', 'post_login', 'get_signup', 'post_signup']  
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')
  
@app.route('/login')
def get_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def post_login():
    email = request.form.get('email')
    password = request.form.get('pw')
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        session['email'] = email
        flash("Login Successful!")
        return redirect('/')
    else:
        flash("Invalid email or password")
        return redirect('/login')
    
@app.route('/signup')
def get_signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def post_signup():
    email = request.form['email']
    password = request.form['pw']
    verifypw = request.form['verifypw']
    existing_user = User.query.filter_by(email=email).first()

    email_error = ''
    password_error = ''
    verifypw_error = ''
    duplicate_user_error = ''
    # Regex pattern looks for alphanumeric characters - minimum 3, no max; '@' symbol, 
    # at least one alphanumeric, ''.'', at least 2 alphas(case insensitive)
    email_pattern = re.compile(r'[\w]{3,}[@][\w]+[.][a-zA-Z]{2,}')
    email_matched = email_pattern.match(email)
    # Regex pattern checks for non-white space characters - minimum 8, maximum 20
    pw_pattern = re.compile(r'[^\s]{4,20}')
    pw_matched = pw_pattern.match(password)
    
    #verify email
    if not email_matched:
        email_error =  'error'
        flash('This email is not valid', 'error')
    else:
        email = email
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

    if not email_error and not password_error and not verifypw_error and not duplicate_user_error:
        new_user = User(email, password)
        db.session.add(new_user)
        db.session.commit()
        session['email'] = email
        flash('Signup successful!', category='success')
        return redirect('/')
    #TODO: Determine if re-rendering template is needed. 
    else:
        return render_template('signup.html', 
        password_error=password_error, email_error=email_error, verifypw_error=verifypw_error,duplicate_user_error=duplicate_user_error,
        password='', verifypw='', email=email)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route('/')
@app.route('/index')
def index():
    if not request.args:
        authors = User.query
        return render_template('index.html', authors=authors)
    else:
        author_id = int(request.args.get('id'))
        posts = Post.query.filter_by(author_id=author_id).all()
        return render_template('displayposts.html', posts=posts)


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
    author = User.query.filter_by(email=session['email']).first()

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