from flask import render_template, url_for
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': '123'}
    posts = [
        {
            'author': {'username': 'A'},
            'body': 'Yes'
        },
        {
            'author': {'username': 'B'},
            'body': 'No'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/page1')
def page1():
    return render_template('page1.html')