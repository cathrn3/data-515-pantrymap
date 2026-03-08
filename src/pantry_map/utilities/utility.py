from math import radians, sin, cos, sqrt, atan2, pi
import hashlib
import numpy as np
from geopy.geocoders import Nominatim

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

def validate_address(input_text):
    """Validate that the address input is not empty."""
    if not input_text.strip():
        return False, "Address cannot be empty."
    return True, ""

def geocode_address(address):
    """Convert a user-entered address into latitude and longitude using Geopy."""
    geolocator = Nominatim(user_agent="pantrymap_app")
    try:
        location = geolocator.geocode(address)
        if location is not None:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None