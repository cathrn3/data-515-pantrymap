import pandas as pd

def load_transit_data(gtfs_folder):
    # Added low_memory=False to prevent DtypeWarnings
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt", low_memory=False)
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt", low_memory=False)
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt", low_memory=False)
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt", low_memory=False)
    calendar = pd.read_csv(f"{gtfs_folder}/calendar.txt", low_memory=False)
    shapes = pd.read_csv(f"{gtfs_folder}/shapes.txt", low_memory=False)

    # Returning 6 items now
    return stops, routes, trips, stop_times, calendar, shapes


def clean_stops(stops):
    stops = stops.dropna(subset=["stop_lat", "stop_lon"])
    stops["stop_name"] = stops["stop_name"].str.strip().str.title()
    stops = stops.drop_duplicates(subset=["stop_id"])

    return stops


def clean_shapes(shapes):

    shapes = shapes.dropna(subset=["shape_pt_lat", "shape_pt_lon"])
    # Sort by shape_id and sequence so the lines draw in the correct order
    shapes = shapes.sort_values(["shape_id", "shape_pt_sequence"])
    return shapes


def filter_active_services(trips, calendar):
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
    # GTFS route types
    # 3 = Bus, 0 = Tram/light rail
    routes = routes[routes["route_type"].isin([3, 0])]
    return routes

def get_active_stops(stops, trips, stop_times):
    active_trips = trips["trip_id"].unique()

    stop_times = stop_times[stop_times["trip_id"].isin(active_trips)]

    active_stop_ids = stop_times["stop_id"].unique()

    stops = stops[stops["stop_id"].isin(active_stop_ids)]

    return stops

def get_relevant_shapes(shapes, trips):
    """
    New function to filter shapes down to only those used by 
    the active trips you've already filtered.
    """
    active_shape_ids = trips["shape_id"].unique()
    shapes = shapes[shapes["shape_id"].isin(active_shape_ids)]
    return shapes