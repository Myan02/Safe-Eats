import os
from pyogrio import set_gdal_config_options

base_directory = os.path.abspath(os.path.dirname(__file__))

class Config():
   inspection_data = base_directory + '/data_files/inspection.csv'
   nyc_map = base_directory + '/data_files/geo_export_27950661-410e-437e-b18e-b7a631653f57.shp'

         