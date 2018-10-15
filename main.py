from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True   
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET', 'POST'])
@app.route('/blog', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Post(title, body)
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/newpost')
def add_post():
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()