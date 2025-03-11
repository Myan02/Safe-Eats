import tkinter as tk
from tkinter import messagebox
from geopy.geocoders import Nominatim
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import Config
from heatmap import export_heatmap

# Retrieve the heatmap and make modifications
def update_heatmap():
    
    # get updated heatmap
    gdf = export_heatmap(need_export=False)
    
    
    # get the user input address from Tkinter label
    address = entry.get()
    if not address:
        # draw initial heatmap if no address is present
        Heatmap.draw_heatmap(gdf)
        return
    
    # convert user address into coordinates
    geolocator = Nominatim(user_agent="geo_app")
    location = geolocator.geocode(address)

    # update the heatmap if the location exists
    if location:
        
        # returns a list of matchine zipcodes
        zipcode = df[(df['Latitude'].round(2) == round(location.latitude, 2)) & 
                     (df['Longitude'].round(2) == round(location.longitude, 2))]['ZIPCODE'].values

        # 0 length means no zipcode was found
        if len(zipcode) == 0:
            messagebox.showerror("Error", "No matching ZIP code found, please try another address")
            return

        zipcode = int(zipcode[0])   # convert zipcode list to a single integer value

        # get the shape of the user's zipcode
        zipcode_geometry = gdf[gdf['modzcta'] == zipcode].geometry

        # continue if the zipcode shape exists
        if zipcode_geometry.empty:
            messagebox.showerror("Error", "Zipcode not found in map data.")
            return

        Heatmap_Zoomed.draw_heatmap(gdf, zipcode, zipcode_geometry)
    else:
        messagebox.showerror("Error", "address not found, please try another address")

# configure and update GUI canvas for plot
def update_canvas(fig):
    global canvas
    if 'canvas' in globals():
        canvas.get_tk_widget().destroy()  # remove old canvas
    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
def close_window():
    root.destroy()
    
# base class for heatmaps
class Heatmap:
    def draw_heatmap(gdf):
        
        # plot heatmap in window
        fig, ax = plt.subplots(figsize=(7, 7))
        gdf.plot(column='GRADE', cmap='coolwarm_r', linewidth=0.4, ax=ax, edgecolor='0.4', legend=True)

        ax.set_title(f"NYC Restaurant Inspection Heatmap")

        # update window canvas element
        update_canvas(fig)

# inherited class for zooming into heatmaps
class Heatmap_Zoomed(Heatmap):
    def draw_heatmap(gdf, zipcode, zipcode_geometry):
        
         # get bounding box to zoom in
        min_x, min_y, max_x, max_y = zipcode_geometry.total_bounds

        # plot heatmap in window
        fig, ax = plt.subplots(figsize=(7, 7))
        gdf.plot(column='GRADE', cmap='coolwarm_r', linewidth=0.4, ax=ax, edgecolor='0.4', legend=True)

        # outline the selected zipcode 
        gdf[gdf['modzcta'] == zipcode].plot(ax=ax, edgecolor='black', linewidth=1, facecolor="none")

        # zoom into the zipcode area
        ax.set_xlim(min_x - 0.01, max_x + 0.01)
        ax.set_ylim(min_y - 0.01, max_y + 0.01)

        ax.set_title(f"NYC Restaurant Inspection Heatmap (ZIP: {zipcode})")

        # update window canvas element
        update_canvas(fig)

    

# create the main window
root = tk.Tk()
root.title("NYC Restaurant Inspection Heatmap")
root.geometry("600x600")    # window size

# GUI elements on the window
tk.Label(root, text="Enter Address:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

close_button = tk.Button(root, text="exit", command=close_window)
close_button.pack()

# entry button to get user input
tk.Button(root, text="Get Result", command=update_heatmap).pack(pady=5)

# read inspection data
df = pd.read_csv(Config.inspection_data)

# run the GUI loop
root.mainloop()
