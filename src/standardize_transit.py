"""
Standardization script for transit agency datasets.

This module provides functions to standardize transit data (stops, routes,
trips, stop times, and shapes) for different transit agencies.
"""

import os
from transit_preprocessing import (
    load_transit_data,
    clean_stops,
    clean_shapes,
    filter_active_services,
    filter_relevant_routes,
    get_active_stops,
    get_relevant_shapes
)

def standardize_agency(gtfs_folder, output_prefix):
    """
    Standardize one transit agency dataset including shape data.

    Args:
        gtfs_folder (str): Path to the folder containing GTFS files.
        output_prefix (str): Prefix for the generated CSV files.
    """
    # 1. Load data
    stops, routes, trips, stop_times, calendar, shapes = load_transit_data(gtfs_folder)

    # 2. Keep only relevant routes (bus + rail)
    routes = filter_relevant_routes(routes)

    # 3. Filter trips by route
    trips = trips[trips["route_id"].isin(routes["route_id"])]

    # 4. Filter trips by Weekday services
    trips = filter_active_services(trips, calendar)

    # 5. Filter shapes to only those used by active trips
    shapes = get_relevant_shapes(shapes, trips)
    shapes = clean_shapes(shapes)

    # 6. Active stop times
    stop_times = stop_times[stop_times["trip_id"].isin(trips["trip_id"])]

    # 7. Active stops
    stops = get_active_stops(stops, trips, stop_times)

    # 8. Clean stop names and coordinates
    stops = clean_stops(stops)

    # 9. Save standardized outputs
    output_dir = "data_preprocessing/processed"
    os.makedirs(output_dir, exist_ok=True)

    stops.to_csv(f"{output_dir}/{output_prefix}_stops.csv", index=False)
    trips.to_csv(f"{output_dir}/{output_prefix}_trips.csv", index=False)
    stop_times.to_csv(f"{output_dir}/{output_prefix}_stop_times.csv", index=False)
    shapes.to_csv(f"{output_dir}/{output_prefix}_shapes.csv", index=False)

    print(f"✅ {output_prefix} standardized and saved (including shapes).")

if __name__ == "__main__":
    # Ensure the directory exists
    os.makedirs("data/processed", exist_ok=True)

    # -------- KING COUNTY --------
    standardize_agency(
        gtfs_folder="data_preprocessing/data/king_county",
        output_prefix="king_county"
    )

    # -------- SOUND TRANSIT --------
    standardize_agency(
        gtfs_folder="data_preprocessing/data/sound_transit",
        output_prefix="sound_transit"
    )
