"""
Preprocessing logic for GTFS transit data.

This module provides helper functions to load, clean, and filter various
GTFS components like stops, routes, trips, stop times, and shapes.
"""

import pandas as pd

def load_transit_data(gtfs_folder):
    """
    Load GTFS data from a specified folder.

    Args:
        gtfs_folder (str): The directory containing GTFS txt files.

    Returns:
        tuple: (stops, routes, trips, stop_times, calendar, shapes) dataframes.
    """
    # Added low_memory=False to prevent DtypeWarnings
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt", low_memory=False)
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt", low_memory=False)
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt", low_memory=False)
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt", low_memory=False)
    calendar = pd.read_csv(f"{gtfs_folder}/calendar.txt", low_memory=False)
    shapes = pd.read_csv(f"{gtfs_folder}/shapes.txt", low_memory=False)

    return stops, routes, trips, stop_times, calendar, shapes

def clean_stops(stops):
    """
    Clean the stops dataframe by dropping NAs and standardizing names.

    Args:
        stops (pd.DataFrame): The stops dataframe.

    Returns:
        pd.DataFrame: The cleaned stops dataframe.
    """
    stops = stops.dropna(subset=["stop_lat", "stop_lon"])
    stops["stop_name"] = stops["stop_name"].str.strip().str.title()
    stops = stops.drop_duplicates(subset=["stop_id"])

    return stops

def clean_shapes(shapes):
    """
    Clean and sort the shapes dataframe.

    Args:
        shapes (pd.DataFrame): The shapes dataframe.

    Returns:
        pd.DataFrame: The cleaned and sorted shapes dataframe.
    """
    shapes = shapes.dropna(subset=["shape_pt_lat", "shape_pt_lon"])
    # Sort by shape_id and sequence so the lines draw in the correct order
    shapes = shapes.sort_values(["shape_id", "shape_pt_sequence"])
    return shapes

def filter_active_services(trips, calendar):
    """
    Filter trips to only include active weekday services.

    Args:
        trips (pd.DataFrame): The trips dataframe.
        calendar (pd.DataFrame): The calendar dataframe.

    Returns:
        pd.DataFrame: Filtered trips dataframe.
    """
    active_services = calendar[
        (calendar["monday"] == 1) |
        (calendar["tuesday"] == 1) |
        (calendar["wednesday"] == 1) |
        (calendar["thursday"] == 1) |
        (calendar["friday"] == 1)
    ]

    trips = trips[trips["service_id"].isin(active_services["service_id"])]

    return trips

def filter_relevant_routes(routes):
    """
    Filter routes to only include bus (3) and tram/light rail (0).

    Args:
        routes (pd.DataFrame): The routes dataframe.

    Returns:
        pd.DataFrame: Filtered routes dataframe.
    """
    # GTFS route types: 3 = Bus, 0 = Tram/light rail
    routes = routes[routes["route_type"].isin([3, 0])]
    return routes

def get_active_stops(stops, trips, stop_times):
    """
    Filter stops to only those associated with active trips.

    Args:
        stops (pd.DataFrame): The stops dataframe.
        trips (pd.DataFrame): The trips dataframe.
        stop_times (pd.DataFrame): The stop_times dataframe.

    Returns:
        pd.DataFrame: Filtered stops dataframe.
    """
    active_trips = trips["trip_id"].unique()
    stop_times_filtered = stop_times[stop_times["trip_id"].isin(active_trips)]
    active_stop_ids = stop_times_filtered["stop_id"].unique()
    stops_filtered = stops[stops["stop_id"].isin(active_stop_ids)]

    return stops_filtered

def get_relevant_shapes(shapes, trips):
    """
    Filter shapes down to only those used by the active trips.

    Args:
        shapes (pd.DataFrame): The shapes dataframe.
        trips (pd.DataFrame): The filtered trips dataframe.

    Returns:
        pd.DataFrame: Filtered shapes dataframe.
    """
    active_shape_ids = trips["shape_id"].unique()
    shapes_filtered = shapes[shapes["shape_id"].isin(active_shape_ids)]
    return shapes_filtered
