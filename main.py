from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True   
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.String(120), nullable=False)

    def __init__(self, title, body):
        self.title = title
        self.body = body

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
            title_error = "This field is required."
            title = ''
        else:
            title = title
            title_error = title_error
    
        if not body:
            body_error = "This field is required."
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
            posts = Post.query.all()
            return render_template('index.html', posts=posts)
        else:
            post_id = int(request.args.get('id'))
            post = Post.query.get(post_id)
            return render_template('displaypost.html',title=post.title, body=post.body)

@app.route('/newpost')
def add_post():
    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()