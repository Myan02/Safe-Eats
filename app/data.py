# Script created to handle all data manipulations, filters, and calculations
# Written by Michael Baburyan April 2025
'''
INSPECTION DATA TYPE INFO:
    DBA : object
    BORO: object
    ZIPCODE: int
    CUISINE DESCRIPTION: object
    INSPECTION DATE: datetime64[ns] (numpy datetime)
    SCORE: int
    GRADE: object
    LATITUDE: float
    LONGITUDE: float

GEOJSON DATA TYPE INFO:
    MODZCTA: object
    LABEL: object
    ZCTA: object
    POP_EST: object
    GEOMETRY: geometry
    
AVERAGE GRADE TYPE INFO:
    ZIPCODE: int
    AVERAGE_GRADE: float
    COLOR: object
'''

import os
import pandas as pd
import geopandas as gpd
from sodapy import Socrata
from matplotlib import colors

class Inspections():
    
    # run before the app instance is even instantiated
    def __init__(self) -> None:
        
        # initialize all dataframes
        self.inspections_df = self.init_data_using_csv()
        self.zipcode_borders_gdf = self.init_borders_using_geojson()
        self.average_grades_per_zipcode_df = self.init_average_grades()
    
    
    # default init, data is from March 2025
    def init_data_using_csv(self) -> pd.DataFrame:
        
        try:
            if __name__ == '__main__':
                
                # for debugging, I read the file staright up by running this script alone
                results = pd.read_csv('./static/data_files/nyc_restaurant_inspections_march_2025.csv')
                
            else:
                results = pd.read_csv('./app/static/data_files/nyc_restaurant_inspections_march_2025.csv')
        except FileNotFoundError:
            print('inspections data does not exist, maybe your filepath is wrong')
        except Exception as e:
            print(f'something went wrong trying to read inspections file: \n {e}')
            
        # we only care about these cols, everything else is bad, also rename them
        results = results[['DBA', 'BORO', 'ZIPCODE', 'CUISINE DESCRIPTION', 'INSPECTION DATE', 'SCORE', 'GRADE', 'Latitude', 'Longitude']]
        results = results.rename(columns={'DBA': 'dba',     
                                          'BORO': 'boro',   
                                          'ZIPCODE': 'zipcode',     
                                          'CUISINE DESCRIPTION': 'cuisine description',
                                          'INSPECTION DATE': 'inspection date',
                                          'SCORE': 'score',
                                          'GRADE': 'grade',
                                          'Latitude': 'latitude',
                                          'Longitude': 'longitude'})
        
        # # get all rows above 2015 since all other rows are not real values
        results['inspection date'] = pd.to_datetime(results['inspection date'])     # format= Year-Month-Day
        results = results[results['inspection date'] >= '2015-01-01']
        
        # only keep inspection rows where they were graded A, B, C
        results = results[(results['grade'] == 'A') | (results['grade'] == 'B') | (results['grade'] == 'C')]
        
        # drop the rows where there is a null value in these columns
        results = results.dropna(subset=['dba', 'zipcode', 'inspection date', 'score', 'grade', 'latitude', 'longitude'])
        
        # convert all scores and zipcodes to integers to get rid of that pesky decimal
        results = results.astype({
            'zipcode': int,
            'score': int
        })
        
        # return pandas dataframe (NOT DICT)
        # we do this so that we can do more filters on the data before passing it over to the application
        return results
    
    
    # default init, border data is from 2010 Covid 19 zipcode geometry
    def init_borders_using_geojson(self) -> pd.DataFrame:
        
        try:
            if __name__ == '__main__':
                
                # for debugging, I read the file straight up by running this script alone
                results = gpd.read_file('./static/data_files/nyc_zipcode_borders.geojson') 
                
                # remove the updated geojson file if it exists, in case something weird happens so every app starts fresh
                if os.path.exists('./static/data_files/nyc_zipcode_borders_with_grades.geojson'):
                    os.remove('./static/data_files/nyc_zipcode_borders_with_grades.geojson')
                
            else:
                results = gpd.read_file('./app/static/data_files/nyc_zipcode_borders.geojson')  
                
                 # remove the updated geojson file if it exists, in case something weird happens so every app starts fresh
                if os.path.exists('./app/static/data_files/nyc_zipcode_borders_with_grades.geojson'):
                    os.remove('./app/static/data_files/nyc_zipcode_borders_with_grades.geojson')    
      
        except FileNotFoundError:
            print('geojson data does not exist, maybe your filepath is wrong')
        except Exception as e:
            print(f'something went wrong trying to read geojson file: \n {e}')
        
        # rename each column to be lowercase, matching the other df columns in the app
        results = results.rename(columns={'MODZCTA': 'modzcta',
                                          'LABEL': 'label',
                                          'ZCTA': 'zcta',
                                          'POP_EST': 'pop_est',
                                          'GEOMETRY': 'geometry'})
            
        # drop the random row that has zipcode 99999
        results = results[results['modzcta'] < str(99999)]
        
        # return geopandas dataframe (NOT DICT)
        # we do this so that we can do more filters on the data before passing it over to the application
        return results
    
    
    # default init, create a dataframe to hold average grades per zipcode
    # by default, add values to geojson file
    def init_average_grades(self, add_to_geojson=True) -> pd.DataFrame:
        
        # check to make sure that the main inspection results exist
        if self.inspections_df is None:
            raise Exception('Trying to create average grades dataframe but inspections doesn\'t exist...')
        
        # adds a color value to each zipcode and average grade
        def add_color_to_zipcodes(results: pd.DataFrame) -> pd.DataFrame:
            
            # add a color value for each floating point value
            cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['blue', 'green', 'orange'])
            norm = colors.Normalize(vmin=1, vmax=3)
            
            results['color'] = results['average_grade'].apply(
                lambda x: colors.rgb2hex(tuple(cmap(norm(x))[:3]))
            )
            
            return results
        
        # exports an updated geojson file with grades and colors
        def add_values_to_geojson(results: pd.DataFrame) -> None:
            
            # check to make sure the zipcode borders gdf exists before proceding
            if self.zipcode_borders_gdf is None:
                raise Exception('Trying to add values to zipcode border dataframe but zipcode borders doesn\'t exist...')
            
            # convert a temporary df to str types in order for it to be compatible with geojson data
            temporary_results_df = results.astype({
                'zipcode': str,
                'average_grade': str
            })

            # merge average grades into geojson file
            self.zipcode_borders_gdf = self.zipcode_borders_gdf.merge(
                temporary_results_df, left_on='modzcta', right_on='zipcode', how='left'
            )
            
            # drop extra zipcode column created from merge
            self.zipcode_borders_gdf.drop(columns=['zipcode'], inplace=True)

            # export as file
            if __name__ == '__main__':
                # debugging
                self.zipcode_borders_gdf.to_file('./static/data_files/nyc_zipcode_borders_with_grades.geojson', driver='GeoJSON')
            else:
                self.zipcode_borders_gdf.to_file('./app/static/data_files/nyc_zipcode_borders_with_grades.geojson', driver='GeoJSON')

        # lower is better!
        grade_to_value = {
            'A': 1,
            'B': 2,
            'C': 3,
        }
        
        # create a copy of the dataframe's important cols for this query
        results = self.inspections_df[['zipcode', 'grade']].copy()
        
        # map each grade to a dedicated value
        results['average_grade'] = results['grade'].map(grade_to_value)
        
        # average value for each zipcode, lower is better
        results = results.groupby('zipcode')['average_grade'].mean().reset_index()
        
        # add color values to each zipcode grade
        results = add_color_to_zipcodes(results)
        
        if add_to_geojson:
            add_values_to_geojson(results)

        
        return results
    
    
    # convert any dataframe to a dictionary, useful for displaying json data 
    @staticmethod
    def convert_df_to_records(df) -> dict:
        return df.to_dict(orient='records')
    
    # return all inspection data as dictionary records
    def get_inspections(self) -> dict:
        return self.convert_df_to_records(self.inspections_df)
    
    # return all zipcode borders from geojson file as dictionary records
    def get_zipcode_borders(self) -> dict:
        return self.convert_df_to_records(self.zipcode_borders_gdf)
    
    # return average grade per zipcode, along with dedicated colors
    def get_average_grades(self) -> dict:
        return self.convert_df_to_records(self.average_grades_per_zipcode_df)









    
    
#     # returns one row for each restaurant, useful for displaying markers on each restaurant
#     def get_unique_restaurant_inspections(self):
#         # get all uniqye restaurants
#         unique_restaurants = self.results_df.drop_duplicates(subset=['dba'], keep='first')
        
#         # sort values in ascending order of restaurant name
#         unique_restaurants_sorted = unique_restaurants.sort_values(by='dba')
        
#         # fill in blank values so that javascript doesn't freak out
#         unique_restaurants_sorted_and_filled = unique_restaurants_sorted.fillna('empty')
        
#         return unique_restaurants_sorted_and_filled.to_dict(orient='records')
    
    


    
