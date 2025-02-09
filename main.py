# Main script starting the data organization
import data

# change these coords to anything in nyc
lat = 40.82015
lon = -73.94931

# df = data.get_data(zipcode=11361, limit=25)
df = data.get_data(latitude=lat, longitude=lon, coord_range=0.01, limit=25)

print(df)

