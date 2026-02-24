import pandas as pd


def combine_transit():

    # Load standardized data
    king_stops = pd.read_csv("data/processed/king_county_stops.csv")
    sound_stops = pd.read_csv("data/processed/sound_transit_stops.csv")

    king_trips = pd.read_csv("data/processed/king_county_trips.csv")
    sound_trips = pd.read_csv("data/processed/sound_transit_trips.csv")

    king_stop_times = pd.read_csv("data/processed/king_county_stop_times.csv")
    sound_stop_times = pd.read_csv("data/processed/sound_transit_stop_times.csv")

    # Combine
    all_stops = pd.concat([king_stops, sound_stops]).drop_duplicates()
    all_trips = pd.concat([king_trips, sound_trips]).drop_duplicates()
    all_stop_times = pd.concat([king_stop_times, sound_stop_times]).drop_duplicates()

    # Save
    all_stops.to_csv("data/processed/all_stops.csv", index=False)
    all_trips.to_csv("data/processed/all_trips.csv", index=False)
    all_stop_times.to_csv("data/processed/all_stop_times.csv", index=False)

    print("✅ Transit systems combined successfully.")


if __name__ == "__main__":
    combine_transit()