from transit_preprocessing import (
    load_transit_data,
    clean_stops,
    filter_active_services,
    filter_relevant_routes,
    get_active_stops
)

def main():
    # 1️⃣ Set GTFS folder path
    gtfs_folder = "data/sound_transit"  # change if needed

    print("Loading transit data...")
    stops, routes, trips, stop_times, calendar = load_transit_data(gtfs_folder)

    print("Cleaning stops...")
    stops = clean_stops(stops)

    print("Filtering active weekday services...")
    trips = filter_active_services(trips, calendar)

    print("Filtering relevant routes (bus + rail)...")
    routes = filter_relevant_routes(routes)

    print("Getting active stops...")
    stops = get_active_stops(stops, trips, stop_times)

    print("Saving cleaned stops...")
    stops.to_csv("data/clean_sound_transit_stops.csv", index=False)

    print("Transit preprocessing complete!")

if __name__ == "__main__":
    main()