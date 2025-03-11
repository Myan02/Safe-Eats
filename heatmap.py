# This script exports a heatmap of NYC based on each zipcode's average inspection grade 
# It can run on its own or be used as a module
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from config import Config



def export_heatmap(need_export):
    # read the data
    df = pd.read_csv(Config.inspection_data)
    gdf = gpd.read_file(Config.nyc_map)

    # filter data
    df = df[['DBA', 'ZIPCODE', 'GRADE', 'Latitude', 'Longitude']]           # get relevant cols
    df.rename(columns={'ZIPCODE': 'modzcta'}, inplace=True)                 # change zipcode col name to modzcta to keep it consistent with the geo data
    df = df.dropna()                                                        # drop blank value rows
    df['modzcta'] = df['modzcta'].astype('int')                             # convert zipcodes from float to int

    # geo data filter
    gdf = gdf.dropna()                                                      # drop empty rows                                              
    gdf['modzcta'] = gdf['modzcta'].astype('int')                           # change modzcta type from object to int

    # convert letter grades to numerical values
    grade_to_value = {'A': 1, 'B':2, 'C':3, 'N': 0, 'Z': 0, 'P': 0}         # set all pending grades to 0 to delete later
    df['GRADE'] = df['GRADE'].map(grade_to_value)                           # set each letter grade to its corresponding value
    df = df[df['GRADE'] != 0]                                               # drop all pending grades so they don't skew our map

    # aggregate values per zipcode
    avg_grades = df.groupby('modzcta')['GRADE'].mean().reset_index()        # get the average grades in each zip code
    gdf = gdf.merge(avg_grades, on='modzcta', how='left')                   # merge the geolocational data with the grade data

    if need_export:
        # plot configuration
        fig, ax = plt.subplots(1, figsize=(10, 10))                             # create the figure and set the size
        plt.xticks(rotation=90)                                                 # set the rotation of the plot

        gdf.plot(column='GRADE', cmap='coolwarm_r', linewidth=0.4, ax=ax, edgecolor='0.4', legend=True)

        plt.title('average restaurant grade in each NYC zipcode')

        plt.savefig('plot.png')
        plt.show()
    else:
        # return the heatmap to be displayed without a simple plot
        return gdf


# Exports the heatmap as a png if the user runs this module standalone
if __name__ == '__main__':
   export_heatmap(need_export=True)


