"""Flask route handlers for the application."""
from flask import Blueprint, render_template, request, current_app, jsonify
from main_app.utils.search import search_restaurants
import logging

# Data analysis and visualization imports
from main_app.plots import total_inspections
from main_app.plots import critical_violations
from main_app.plots import average_score
from main_app.plots import worst_borough
from main_app.plots import create_grade_pie_chart
from main_app.plots import create_grade_bar_chart
from main_app.plots import create_grade_boro_bar_chart
from main_app.plots import create_average_score_boro
from main_app.plots import create_critical_boro_bar_chart
from main_app.plots import create_cuisines_chart
from main_app.plots import create_cuisines_percentage_chart
from main_app.plots import create_violations_per_cuisine_chart
from main_app.plots import create_latest_violations_per_cuisine_chart
from main_app.plots import create_avg_violations_by_cuisine_and_borough_chart
from main_app.plots import create_violation_code_treemap
from main_app.plots import create_most_critical_violation
from main_app.plots import create_most_non_critical_violation
from main_app.plots import create_worst_month_for_violations
from main_app.plots import create_worse_restaurant_boro_chart
from main_app.plots import create_top_5_safest_cuisines



bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the main search page."""
    return render_template('index.html', mapbox_token=current_app.config['MAPBOX_TOKEN'])

@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@bp.route('/search', methods=['POST'])
def search():
    """Handle restaurant search requests."""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    address = data.get('address', '').strip()
    
    try:
        response_data = search_restaurants(address)
        return current_app.response_class(
            response=current_app.json.dumps(response_data),
            mimetype='application/json'
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500
    

# data visualization route
@bp.route('/graphs')
def graphs():
    """Render the graphs page."""
    grade_pie = create_grade_pie_chart()
    grade_bar = create_grade_bar_chart()
    boro_bar = create_grade_boro_bar_chart()
    cuisines_bar = create_cuisines_chart()
    cuisines_percentage = create_cuisines_percentage_chart()
    violations_per_cuisine = create_violations_per_cuisine_chart()
    latest_violations_per_cuisine = create_latest_violations_per_cuisine_chart()
    avg_violations_by_cuisine_and_borough = create_avg_violations_by_cuisine_and_borough_chart()
    avg_score_boro = create_average_score_boro()
    critical_boro = create_critical_boro_bar_chart()
    violation_code = create_violation_code_treemap()
    all_inspections = "{:,}".format(total_inspections())
    critical = "{:,}".format(critical_violations())
    avg_score = average_score()
    bad_borough = worst_borough()
    worst_month = create_worst_month_for_violations()
    critical_violation = create_most_critical_violation()
    non_critical_violation = create_most_non_critical_violation()
    worst_restaurant_boro = create_worse_restaurant_boro_chart()
    top_5_safest_cuisines = create_top_5_safest_cuisines()
    return render_template('graphs.html',
                           all_inspections=all_inspections,
                           critical=critical,
                           avg_score=avg_score,
                           bad_borough=bad_borough, 
                           grade_pie=grade_pie, 
                           grade_bar=grade_bar, 
                           boro_bar=boro_bar,
                           avg_score_boro=avg_score_boro,
                           critical_boro=critical_boro,
                           cuisines_bar=cuisines_bar,
                           cuisines_percentage=cuisines_percentage,
                           violations_per_cuisine=violations_per_cuisine,
                           latest_violations_per_cuisine = latest_violations_per_cuisine,
                           avg_violations_by_cuisine_and_borough=avg_violations_by_cuisine_and_borough,
                           violation_code=violation_code,
                           worst_month=worst_month,
                           critical_violation=critical_violation,
                           non_critical_violation=non_critical_violation,
                           worst_restaurant_boro=worst_restaurant_boro,
                           top_5_safest_cuisines=top_5_safest_cuisines
                           )
