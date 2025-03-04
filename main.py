import tkinter as tk
import geopy
from tkinter import messagebox, scrolledtext
from geopy.geocoders import Nominatim
import data

def get_coordinates():
    address = entry.get()
    if not address:
        messagebox.showerror("Error", "Please enter an address.")
        return
    
    geolocator = Nominatim(user_agent="geo_app")
    location = geolocator.geocode(address)

    if location:
        df = data.get_data(latitude=location.latitude, longitude=location.longitude, coord_range=0.01, limit=10)    
        result = f"Latitude: {location.latitude}\nLongitude: {location.longitude}\n\n{df}"
        result_textbox.config(state=tk.NORMAL)
        result_textbox.delete(1.0, tk.END)
        result_textbox.insert(tk.END, result)
        result_textbox.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Error", "Address not found.")

#Sample 160 convent ave, new york, ny 10031
# Main App
root = tk.Tk()
root.title("Address Coordinates")
root.geometry("400x300")

tk.Label(root, text="Enter Address:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

tk.Button(root, text="Get Result", command=get_coordinates).pack(pady=5)

result_textbox = scrolledtext.ScrolledText(root, width=50, height=10, wrap=tk.WORD, state=tk.DISABLED)
result_textbox.pack(pady=5)

root.mainloop()