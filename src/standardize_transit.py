'''
import pandas as pd
from transit_preprocessing import (
    load_transit_data,
    clean_stops,
    filter_active_services,
    filter_relevant_routes,
    get_active_stops
)


def standardize_agency(gtfs_folder, output_prefix):
    """
    Standardize one transit agency dataset
    """

    stops, routes, trips, stop_times, calendar = load_transit_data(gtfs_folder)

    # 1. Keep only relevant routes (bus + rail)
    routes = filter_relevant_routes(routes)

    # 2. Filter trips
    trips = trips[trips["route_id"].isin(routes["route_id"])]

    # 3. Weekday services
    trips = filter_active_services(trips, calendar)

    # 4. Active stop times
    stop_times = stop_times[stop_times["trip_id"].isin(trips["trip_id"])]

    # 5. Active stops
    stops = get_active_stops(stops, trips, stop_times)

    # 6. Clean stop names and coordinates
    stops = clean_stops(stops)

    # 7. Save standardized outputs
    stops.to_csv(f"data/processed/{output_prefix}_stops.csv", index=False)
    trips.to_csv(f"data/processed/{output_prefix}_trips.csv", index=False)
    stop_times.to_csv(f"data/processed/{output_prefix}_stop_times.csv", index=False)

    print(f"✅ {output_prefix} standardized and saved.")


if __name__ == "__main__":

    # -------- KING COUNTY --------
    standardize_agency(
        gtfs_folder="data/king_county",
        output_prefix="king_county"
    )

    # -------- SOUND TRANSIT --------
    standardize_agency(
        gtfs_folder="data/sound_transit",
        output_prefix="sound_transit"
    )
'''

import pandas as pd
from transit_preprocessing import (
    load_transit_data,
    clean_stops,
    clean_shapes,            # New function
    filter_active_services,
    filter_relevant_routes,
    get_active_stops,
    get_relevant_shapes      # New function
)

def standardize_agency(gtfs_folder, output_prefix):
    """
    Standardize one transit agency dataset including shape data.
    """
    # 1. Updated loader to unpack 6 items instead of 5
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
    stops.to_csv(f"data_preprocessing/processed/{output_prefix}_stops.csv", index=False)
    trips.to_csv(f"data_preprocessing/processed/{output_prefix}_trips.csv", index=False)
    stop_times.to_csv(f"data_preprocessing/processed/{output_prefix}_stop_times.csv", index=False)
    # Save the new shapes file
    shapes.to_csv(f"data_preprocessing/processed/{output_prefix}_shapes.csv", index=False)

    print(f"✅ {output_prefix} standardized and saved (including shapes).")

if __name__ == "__main__":
    # Ensure the directory exists
    import os
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