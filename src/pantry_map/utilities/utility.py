from math import radians, sin, cos, sqrt, atan2, pi
import hashlib
import numpy as np
from geopy.geocoders import Nominatim
import pandas as pd

def color_from_id(route_id):
    """Generate a color from the route_id"""
    hex_hash = hashlib.md5(str(route_id).encode()).hexdigest()
    return f"#{hex_hash[:6]}"

def lat_lon_to_mercator(lat, lon):
    """Convert lat/lon to Web Mercator projection"""
    k = 6378137
    x = lon * (k * pi/180.0)
    y = np.log(np.tan((90 + lat) * pi/360.0)) * k
    return x, y

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in miles using Haversine formula"""
    radius = 3959
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a_value = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c_value = 2 * atan2(sqrt(a_value), sqrt(1-a_value))
    return round(radius * c_value, 2)

#TODO: add an if else checking if seattle is in the text, if not, add it
#also check if its in seattle, maybe add a red icon for user
def validate_address(input_text):
    """"Validate that the address input is not empty."""

    # Remove leading/trailing whitespace
    address = input_text.strip()

    # Check for empty input
    if not address:
        return False, "Address cannot be empty.", None

    # Ensure the address includes Seattle to increase searching accuracy
    if "seattle" not in address.lower():
        address = f"{address}, Seattle, WA"

    return True, "", address

def geocode_address(address):
    """Convert a user-entered address into latitude and longitude using Geopy."""
    geolocator = Nominatim(user_agent="pantrymap_app")
    try:
        location = geolocator.geocode(address)
        if location is not None:
            lat = location.latitude
            lon = location.longitude

            # Seattle region bounds
            if not (47.0 <= lat <= 48.0 and -123.0 <= lon <= -121.5):
                print("Address is outside the Seattle area.")
                return None, None

            return lat, lon
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

def find_nearest_foodbanks(foodbank_df, user_lat, user_lon, k=5):
    """
    Find the n nearest food banks to a given user location.
    """
    
    # Calculate distance to each food bank
    foodbank_df = foodbank_df.copy() 
    foodbank_df['distance'] = foodbank_df.apply(
        lambda row: calculate_distance(user_lat, user_lon, row['Latitude'], row['Longitude']),
        axis=1
    )
    
    # Sort by distance and return top n
    nearest_df = foodbank_df.sort_values('distance').head(k)
    return nearest_df