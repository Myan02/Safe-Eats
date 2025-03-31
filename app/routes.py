from flask import render_template, jsonify
from app.data import Inspections
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/restaurants')
def get_restaurant():
        
        return jsonify(Inspections.return_grades())

