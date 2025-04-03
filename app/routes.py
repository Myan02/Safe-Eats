from flask import render_template, jsonify, request, send_from_directory
from app import inspection_data
from app import app


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/inspections/<data>')
def get_data(data):
    # if request.method == 'POST':
    #     if data == 'get_average_grades':
    #         print('\n\nreturned properly\n\n')
    #         return jsonify(inspection_data.get_average_grades())
    #     if data == 'get_zipcode_borders':
    #         return jsonify(inspection_data.get_zipcode_borders())
    # else:
    return jsonify(inspection_data.get_average_grades())
    
@app.route('/zipcode_borders/<filename>')
def get_zipcode_borders(filename):
    return send_from_directory('static/data_files', filename)


