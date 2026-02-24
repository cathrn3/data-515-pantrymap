import pandas as pd

def load_transit_data(gtfs_folder):
    stops = pd.read_csv(f"{gtfs_folder}/stops.txt")
    routes = pd.read_csv(f"{gtfs_folder}/routes.txt")
    trips = pd.read_csv(f"{gtfs_folder}/trips.txt")
    stop_times = pd.read_csv(f"{gtfs_folder}/stop_times.txt")
    calendar = pd.read_csv(f"{gtfs_folder}/calendar.txt")

    return stops, routes, trips, stop_times, calendar


def clean_stops(stops):
    stops = stops.dropna(subset=["stop_lat", "stop_lon"])
    stops["stop_name"] = stops["stop_name"].str.strip().str.title()
    stops = stops.drop_duplicates(subset=["stop_id"])

    return stops

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

