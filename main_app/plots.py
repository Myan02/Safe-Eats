import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go



restaurant_data = 'data/restaurant_data.csv'
df = pd.read_csv(restaurant_data)
# Save as Parquet
df.to_parquet('data/restaurant_data.parquet')
# Load from Parquet
df = pd.read_parquet('data/restaurant_data.parquet')


custom_colors = ['#2B7CCC', '#FFAC24', '#45D05E', '#7b6f2b', '#394C54', '#DBCFC6']

# Removing unecessary columns
new_df = df.drop(['Community Board', 'Council District', 'Census Tract','BIN','BBL', 'NTA', 'Location Point1'], axis=1)
# Drop rows where the 'DBA' (restaurant name) is NaN
new_df = new_df.dropna(subset=['DBA'])
# Drop rows if both 'SCORE' and 'GRADE' are NaN
new_df = new_df.dropna(subset=['GRADE', 'SCORE'], how='all')


# Convert 'INSPECTION DATE', 'ZIPCODE' and 'RECORD DATE' to numeric
new_df['INSPECTION DATE'] = pd.to_datetime(new_df['INSPECTION DATE'])
new_df['RECORD DATE'] = pd.to_datetime(new_df['RECORD DATE'])
new_df['ZIPCODE'] = new_df['ZIPCODE'].astype('Int64')  # Nullable int, preserves NaNs
new_df['SCORE'] = new_df['SCORE'].astype('Int64')


# Use conditional updates for missing grades 
new_df.loc[(new_df['GRADE'].isna()) & (new_df['SCORE'] >= 0) & (new_df['SCORE'] <= 13),'GRADE'] = 'A'
new_df.loc[(new_df['GRADE'].isna()) & (new_df['SCORE'] >= 14) & (new_df['SCORE'] <= 27),'GRADE'] = 'B'
new_df.loc[(new_df['GRADE'].isna()) & (new_df['SCORE'] >= 28), 'GRADE'] = 'C'

def total_inspections():
    return len(new_df)

def critical_violations():
    filtered_df = new_df.dropna(subset=['CRITICAL FLAG'])
    return len(filtered_df[filtered_df['CRITICAL FLAG'] == 'Critical'])

def average_score():
    filtered_df = new_df[new_df['SCORE'].notna()]
    return filtered_df['SCORE'].mean().round(2)


def worst_borough():
    avg_scores = new_df.groupby('BORO')['SCORE'].mean().reset_index()
    worst = avg_scores.sort_values(by='SCORE', ascending=False).iloc[0]
    return worst['BORO']


# Create a pie chart
def create_grade_pie_chart():
    # Remove rows with NaN in 'GRADE' column
    filtered_df = new_df.dropna(subset=['GRADE'])
    grade_count = filtered_df.groupby('GRADE').size().reset_index(name='Count')
    grade_count.sort_values(by='GRADE', ascending=True)
    fig = px.pie(
        grade_count,
        names= 'GRADE' ,
        values='Count',
        hole=.3,
        color_discrete_sequence = custom_colors
    )
    fig.update_layout(
    width=500,
    height=500,
    margin=dict(t=100, b=50, l=50, r=50)
    )

    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})

# Create a bar chart
def create_grade_bar_chart():
    filtered_df = new_df.dropna(subset=['GRADE'])
    grade_count = filtered_df.groupby('GRADE').size().reset_index(name='Count')
    grade_count.sort_values(by='GRADE', ascending=True)
    fig = px.bar(
        grade_count.head(3), 
        x= 'GRADE', 
        y='Count',
        hover_data = 'Count',
        color='GRADE',
        labels={'GRADE': 'Grade', 'Count': 'Number of Restaurants'},
        text='Count',
        height=600,
        color_discrete_map = {'A': '#2B7CCC', 'B': '#45D05E', 'C': '#FFAC24'}
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



def create_grade_boro_bar_chart():
    filtered_df = new_df.dropna(subset=['GRADE', 'BORO'])
    grade_count_per_boro = filtered_df.groupby(['GRADE', 'BORO']).size().reset_index(name='Count')
    grade_count_per_boro = grade_count_per_boro[grade_count_per_boro['GRADE'].isin(['A', 'B', 'C'])]
    fig = px.bar(
        grade_count_per_boro.sort_values(by='BORO', ascending=True), 
        x='Count',
        y='BORO',
        color='GRADE',
        labels={'GRADE': 'Grade', 'Count': 'Number of Restaurants', 'BORO': 'Borough'},
        title = 'Distribution of Inspection Grades across all 5 Boroughs',
        color_discrete_map = {'A': '#2B7CCC', 'B': '#45D05E', 'C': '#FFAC24'},
        barmode='group',
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



def create_average_score_boro():
    filtered_df = new_df.dropna(subset=['SCORE', 'BORO'])
    avg_scores = filtered_df.groupby('BORO')['SCORE'].mean().reset_index()
    avg_scores['SCORE'] = avg_scores['SCORE'].round(2)

    fig = px.bar(
        avg_scores,
        x='BORO',
        y='SCORE',
        title='Average Inspection Score by Borough',
        color='BORO',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        xaxis_title='Borough',
        yaxis_title='Average Score',
        showlegend=False
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})


def create_critical_boro_bar_chart():
    filtered_df = new_df[new_df['CRITICAL FLAG'] != 'Not Applicable']
    filtered_df = filtered_df.dropna(subset=['CRITICAL FLAG', 'BORO'])
    critical_count_per_boro = filtered_df.groupby(['CRITICAL FLAG', 'BORO']).size().reset_index(name='Count')
    fig = px.bar(
        critical_count_per_boro.sort_values(by='BORO', ascending=True), 
        x='Count',
        y='BORO',
        color='CRITICAL FLAG',
        labels={'CRITICAL FLAG': 'Critical Flag', 'Count': 'Number of Violations', 'BORO': 'Borough'},
        title = 'Critical Violations across all 5 Boroughs',
        color_discrete_map = {'Critical': '#ef4444', 'Not Critical': '#f59e0c'},
        barmode='group',
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



groups = {
    'American': ['Tex-Mex', 'American', 'Chicken', 'Hamburgers', 'Hotdogs', 'Hotdogs/Pretzels',
                 'Sandwiches', 'Hawaiian', 'Barbecue', 'Bagels/Pretzels', 'Soul Food',
                 'Steakhouse', 'Pancakes/Waffles', 'Sandwiches/Salads/Mixed Buffet', 'New American', 'Californian'],
    'Cafe & Desserts': ['Donuts', 'Coffee/Tea', 'Bakery Products/Desserts', 'Bottled Beverages', 'Nuts/Confectionary'],
    'Juice/Smoothies/Ice-Cream/Fruit Salads/Yogurt': ['Frozen Desserts', 'Juice, Smoothies, Fruit Salads'],
    'South Asian(Indian, Pakistani, Afghan, etc)': ['Indian', 'Bangladeshi', 'Pakistani'],
    'Southeast Asian(Thai, Viet, Malaysia, etc)': ['Thai', 'Southeast Asian', 'Filipino', 'Indonesian'],
    'Mediterranean': ['Greek', 'Turkish', 'Moroccan'],
    'European(Irish, English, German, etc)': ['Portuguese', 'Irish', 'Continental', 'Russian', 'Polish',
                                              'Eastern European', 'English', 'German', 'Czech', 'Scandinavian', 'Basque'],
    'Fusion': ['Creole', 'Fusion', 'Creole/Cajun', 'Cajun', 'Haute Cuisine'],
    'Vegetarian/Vegan': ['Vegetarian', 'Vegan', 'Salads', 'Fruits/Vegetables'],
    'Latin': ['Latin American', 'Peruvian', 'Brazilian', 'Chilean', 'Chimichurri'],
    'Spanish': ['Spanish', 'Tapas'],
    'Middle Eastern': ['Middle Eastern', 'Afghan', 'Armenian', 'Egyptian', 'Iranian'],
    'Specialties': ['Soups', 'Soups/Salads/Sandwiches'],
    'Chinese': ['Chinese', 'Chinese/Cuban'],
    'Asian': ['Chinese/Japanese'],
    'French': ['French', 'New French']
}

# Add individual items that don't belong to a group
individual = {
    'Pizza': 'Pizza',
    'Italian': 'Italian',
    'Japanese': 'Japanese',
    'Jewish/Kosher': 'Jewish/Kosher',
    'Korean': 'Korean',
    'Caribbean': 'Caribbean',
    'African': 'African',
    'Australian': 'Australian',
    'Not Listed/Not Applicable': 'Not Listed/Not Applicable',
    'Other': 'Other'
}

# Create a mapping from individual cuisines to their groups
cuisine_mapping = {c: group for group, cuisines in groups.items() for c in cuisines}
cuisine_mapping.update(individual)

# Apply mapping and clean up
new_df['GROUPED_CUISINE'] = (
    new_df['CUISINE DESCRIPTION']
    .map(cuisine_mapping)
    .fillna('Other')
    .str.strip()
    .str.title()
)

filtered_cuisine_df = new_df[
    ~new_df['GROUPED_CUISINE'].isin([
        'Not Listed/Not Applicable',
        'Other',
        'Unknown',
        'Specialties'
    ])
]

grade_count_per_cuisine = (
    filtered_cuisine_df[filtered_cuisine_df['GRADE'].isin(['A', 'B', 'C'])]
    .groupby(['GRADE', 'GROUPED_CUISINE'])
    .size()
    .reset_index(name='Count')
    .sort_values(by='Count', ascending=False)
)


# Create a bar chart for cuisines
def create_cuisines_chart():
    fig = px.bar(    
        grade_count_per_cuisine.sort_values(by='Count', ascending=False),
        x='Count',
        y='GROUPED_CUISINE',
        color='GRADE',
        labels={'GRADE': 'Grade', 'Count': 'Number of Restaurants', 'GROUPED_CUISINE': 'Cuisine'},
        title='Inspection Grade for All Cuisines',
        color_discrete_map={'A': '#2B7CCC', 'B': '#45D05E', 'C': '#FFAC24'},
        width=1100,  
        height=800   
    )   
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



# Get total count per cuisine
grade_count_per_cuisine['Total Per Cuisine'] = grade_count_per_cuisine.groupby('GROUPED_CUISINE')['Count'].transform('sum')
# Compute the percentage each grade makes up within its cuisine
grade_count_per_cuisine['Percentage'] = (grade_count_per_cuisine['Count'] / grade_count_per_cuisine['Total Per Cuisine']) * 100


# # Create a bar chart for cuisine by percentage
def create_cuisines_percentage_chart():
    fig = px.bar(
        grade_count_per_cuisine.sort_values(by='Percentage', ascending=True),
        y='GROUPED_CUISINE',
        x='Percentage',
        color='GRADE',
        labels={
            'GRADE': 'Grade',
            'Percentage': 'Percentage of Restaurants',
            'GROUPED_CUISINE': 'Cuisine Type'
        },
        title='Distribution of Grades in Each Cuisine',
        color_discrete_map={'A': '#2B7CCC', 'B': '#45D05E', 'C': '#FFAC24'},
        width=1100,
        height=800
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



# Step 1: Group by cuisine and violation
violations_per_cuisine = new_df.groupby(['GROUPED_CUISINE', 'VIOLATION DESCRIPTION']).size().reset_index(name='Violation Count')
violations_per_cuisine = violations_per_cuisine[violations_per_cuisine['GROUPED_CUISINE'] != 'Not Listed/Not Applicable']
violations_per_cuisine = violations_per_cuisine[violations_per_cuisine['GROUPED_CUISINE'] != 'Other']
total_violations_per_cuisine = violations_per_cuisine.groupby('GROUPED_CUISINE')['Violation Count'].sum().reset_index()


# bar chart of violation per cuisine
def create_violations_per_cuisine_chart():
    fig = px.bar(
        total_violations_per_cuisine.sort_values(by='Violation Count', ascending=True),
        x='Violation Count',
        y='GROUPED_CUISINE',
        labels={'Violation Count': 'Number of Violations', 'GROUPED_CUISINE': 'Cuisine'},
        title='Total Violations per Cuisine',
        width=1100,
        height=800,
        color_discrete_sequence=['#8B0000']
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})


# Get latest inspection date per cuisine
latest_dates_by_cuisine = new_df.groupby('GROUPED_CUISINE')['INSPECTION DATE'].max().reset_index()
latest_dates_by_cuisine = latest_dates_by_cuisine[latest_dates_by_cuisine['GROUPED_CUISINE'] != 'Not Listed/Not Applicable']
latest_dates_by_cuisine = latest_dates_by_cuisine[latest_dates_by_cuisine['GROUPED_CUISINE'] != 'Other']
latest_inspections = pd.merge(
    new_df,
    latest_dates_by_cuisine,
    on=['GROUPED_CUISINE', 'INSPECTION DATE']
)
# Keep only rows with real violations
latest_inspections = latest_inspections.dropna(subset=['VIOLATION DESCRIPTION'])
# Count total violations per cuisine
lastest_violations_per_cuisine = latest_inspections.groupby('GROUPED_CUISINE').size().reset_index(name='Latest Violations')

# Bar chart of latest violations per cuisine
def create_latest_violations_per_cuisine_chart():
    fig = px.bar(
        lastest_violations_per_cuisine.sort_values(by='Latest Violations', ascending=True),
        x='Latest Violations',
        y='GROUPED_CUISINE',
        labels={'Latest Violations': 'Number of Violations', 'GROUPED_CUISINE': 'Cuisine'},
        title='Latest Violations per Cuisine',
        width=1100,
        height=800,
        color_discrete_sequence=['#8B0000']
    )
    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})


cuisine_violation_per_boro = (new_df
    .dropna(subset=['VIOLATION DESCRIPTION'])  # Only actual violations
    .groupby(['GROUPED_CUISINE', 'BORO'])['VIOLATION DESCRIPTION']
    .count()
    .reset_index(name='Violation Count')
)

# Count violations (rows) and unique inspections (CAMIS)
violations = (
    new_df
    .groupby(['GROUPED_CUISINE', 'BORO'])
    .agg(
        Total_Violations=('VIOLATION DESCRIPTION', 'count'),
        Total_Inspections=('CAMIS', 'nunique')
    )
    .reset_index()
)

violations['Average_Violations_Per_Inspection'] = (violations['Total_Violations'] / violations['Total_Inspections']).round(2)
violations = violations[violations['GROUPED_CUISINE'] != 'Not Listed/Not Applicable']
violations = violations[violations['GROUPED_CUISINE'] != 'Other']

# Create a bar chart for violations per cuisine and borough
def create_avg_violations_by_cuisine_and_borough_chart():
    fig = px.bar(
        violations.sort_values(by='Average_Violations_Per_Inspection', ascending=True),
        x='Average_Violations_Per_Inspection',
        y='GROUPED_CUISINE',
        color_discrete_sequence=['#8B0000'],
        orientation='h',
        facet_col='BORO',
        labels={'GROUPED_CUISINE': 'Cuisine Type'},
        title='Average Number of Violations per Restaurant by Cuisine and Borough',
        height=800,
        width=1100
    )

    # Remove default axis titles
    fig.update_layout(xaxis_title='')
    fig.for_each_xaxis(lambda axis: axis.update(title=''))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))

    # Custom annotation at the bottom center
    fig.add_annotation(
        text='Average Violations per Inspection',
        xref='paper',
        yref='paper',
        x=0.5,
        y=-0.1,
        font=dict(size=14),
        showarrow=False,
        align='center'
    )

    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})


violation_counts = new_df.dropna(subset=['VIOLATION CODE'])
violation_counts = violation_counts.groupby(['VIOLATION CODE']).size().reset_index(name='Count')

# Create violation code distribution treemap
def create_violation_code_treemap():
    fig = go.Figure(go.Treemap(
        labels=violation_counts['VIOLATION CODE'],
        parents=[""] * len(violation_counts),  # Flat structure (no hierarchy)
        values=violation_counts['Count'],
        marker=dict(colors=violation_counts['Count'], colorscale='RdBu'),
        hovertemplate='<b>Code:</b> %{label}<br><b>Count:</b> %{value}<extra></extra>'
    ))

    fig.update_layout(
        title='Violation Codes Distribution',
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(size=14)
    )

    return pio.to_html(fig, full_html=False, config={'displayModeBar': False})



def create_most_critical_violation():
    filtered_df = new_df.dropna(subset=['CRITICAL FLAG', 'VIOLATION DESCRIPTION'])
    most_common_critical = filtered_df[filtered_df['CRITICAL FLAG'] == 'Critical']['VIOLATION DESCRIPTION'].value_counts().idxmax()
    return most_common_critical

def create_most_non_critical_violation():
    filtered_df = new_df.dropna(subset=['CRITICAL FLAG', 'VIOLATION DESCRIPTION'])
    most_non_common_critical = filtered_df[filtered_df['CRITICAL FLAG'] == 'Not Critical']['VIOLATION DESCRIPTION'].value_counts().idxmax()
    return most_non_common_critical

def create_worst_month_for_violations():
    filtered_df = new_df.dropna(subset=['INSPECTION DATE', 'VIOLATION DESCRIPTION'])
    # Extract full month name
    filtered_df['Month'] = filtered_df['INSPECTION DATE'].dt.strftime('%B')

    # Group by month and count violations
    monthly_counts = filtered_df.groupby('Month')['VIOLATION DESCRIPTION'].size()

    # Reorder months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts = monthly_counts.reindex(month_order)

    # Calculate worst month
    avg = monthly_counts.mean()
    worst_month = monthly_counts.idxmax()
    worst_value = monthly_counts.max()
    percent_above_avg = round((worst_value - avg) / avg * 100)

    worst_month_summary = f"{worst_month} ({percent_above_avg}% higher than average)"
    return worst_month_summary


# def create_top_5_safest_cuisines():
#     filtered_df = new_df.dropna(subset=['SCORE', 'GROUPED_CUISINE'])
#     avg_scores = filtered_df.groupby('GROUPED_CUISINE')['SCORE'].mean().reset_index()
#     avg_scores['SCORE'] = avg_scores['SCORE'].round(2)
#     top_5_safest_cuisines = avg_scores.sort_values(by='SCORE').head(5)
#     return top_5_safest_cuisines

def create_top_5_safest_cuisines():
    filtered_df = new_df.dropna(subset=['GROUPED_CUISINE', 'SCORE'])

     # Exclude cuisines that are "Not Listed/Not Applicable"
    filtered_df = filtered_df[filtered_df['GROUPED_CUISINE'] != 'Not Listed/Not Applicable']
    filtered_df = filtered_df[filtered_df['GROUPED_CUISINE'] != 'Specialties']
    filtered_df = filtered_df[filtered_df['GROUPED_CUISINE'] != 'Other']

    grouped = filtered_df.groupby('GROUPED_CUISINE')['SCORE'].mean().reset_index()
    safest = grouped.sort_values(by='SCORE').head(5)
    return safest.to_dict(orient='records')



def create_worse_restaurant_boro_chart():
    filtered_df = new_df.dropna(subset=['BORO', 'DBA', 'SCORE'])
    filtered_df = filtered_df[filtered_df['GRADE'].isin(['A', 'B', 'C'])]
    worst_per_boro = filtered_df.sort_values(by='SCORE', ascending=False).groupby('BORO').head(1)
    worst_per_boro = worst_per_boro[['DBA', 'BORO', 'SCORE']].reset_index(drop=True)
    return worst_per_boro.to_dict(orient='records')




    





