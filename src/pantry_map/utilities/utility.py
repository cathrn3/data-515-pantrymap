"""
Utility functions for PantryMap calculations and geocoding.

This module contains various helper functions for spatial calculations,
address validation, geocoding, and finding nearest locations.
"""

import hashlib
from math import radians, sin, cos, sqrt, atan2, pi

import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def color_from_id(route_id):
    """
    Generate a hex color code from a route ID using MD5 hashing.

    Args:
        route_id (str or int): The ID of the route.

    Returns:
        str: A hex color string (e.g., '#a1b2c3').
    """
    hex_hash = hashlib.md5(str(route_id).encode()).hexdigest()
    return f"#{hex_hash[:6]}"

def lat_lon_to_mercator(lat, lon):
    """
    Convert latitude and longitude to Web Mercator projection coordinates.

    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.

    Returns:
        tuple: (x, y) coordinates in Web Mercator projection.
    """
    radius_m = 6378137
    coord_x = lon * (radius_m * pi / 180.0)
    coord_y = np.log(np.tan((90 + lat) * pi / 360.0)) * radius_m
    return coord_x, coord_y

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points in miles using Haversine.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: Distance in miles, rounded to 2 decimal places.
    """
    radius_miles = 3959
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a_val = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c_val = 2 * atan2(sqrt(a_val), sqrt(1 - a_val))
    return round(radius_miles * c_val, 2)

def validate_address(input_text):
    """
    Validate that the address input is not empty and append 'Seattle' if missing.

    Args:
        input_text (str): The raw address string entered by the user.

    Returns:
        tuple: (is_valid: bool, error_message: str, cleaned_address: str)
    """
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
    """
    Convert a user-entered address into latitude and longitude using Nominatim.

    Args:
        address (str): The address string to geocode.

    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails.
    """
    geolocator = Nominatim(user_agent="pantrymap_app")
    for _ in range(2):
        try:
            location = geolocator.geocode(address)
            if location is not None:
                lat = location.latitude
                lon = location.longitude

                # Seattle region bounds (rough bounding box)
                if not (47.0 <= lat <= 48.0 and -123.0 <= lon <= -121.5):
                    print(f"Address '{address}' is outside the Seattle area.")
                    return None, None

                return lat, lon
        except (GeocoderTimedOut, Exception) as err:  # pylint: disable=broad-exception-caught
            print(f"Geocoding error for '{address}': {err}")
            continue
    return None, None

def find_nearest_foodbanks(foodbank_df, user_lat, user_lon, k=5):
    """
    Find the k nearest food banks to a given user location.

    Args:
        foodbank_df (pd.DataFrame): Dataframe containing food bank locations.
        user_lat (float): Latitude of the user.
        user_lon (float): Longitude of the user.
        k (int): Number of nearest food banks to return.

    Returns:
        pd.DataFrame: A filtered dataframe containing the k nearest locations,
                      sorted by distance.
    """
    # Calculate distance to each food bank
    foodbank_df_copy = foodbank_df.copy()
    foodbank_df_copy['distance'] = foodbank_df_copy.apply(
        lambda row: calculate_distance(user_lat, user_lon, row['Latitude'], row['Longitude']),
        axis=1
    )

    # Sort by distance and return top k
    nearest_df = foodbank_df_copy.sort_values('distance').head(k)
    return nearest_df
