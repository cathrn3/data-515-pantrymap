"""
Script to combine transit datasets from King County and Sound Transit systems.

This script merges standardized stops, trips, stop times, and shapes from both
systems into unified CSV files.
"""

import pandas as pd

def combine_transit():
    """
    Standardize and merge King County and Sound Transit datasets.
    """
    print("Combining transit datasets...")

    # 1. Load standardized data
    king_stops = pd.read_csv("data_preprocessing/processed/king_county_stops.csv")
    sound_stops = pd.read_csv("data_preprocessing/processed/sound_transit_stops.csv")

    king_trips = pd.read_csv("data_preprocessing/processed/king_county_trips.csv")
    sound_trips = pd.read_csv("data_preprocessing/processed/sound_transit_trips.csv")

    king_stop_times = pd.read_csv("data_preprocessing/processed/king_county_stop_times.csv")
    sound_stop_times = pd.read_csv("data_preprocessing/processed/sound_transit_stop_times.csv")

    king_shapes = pd.read_csv("data_preprocessing/processed/king_county_shapes.csv")
    sound_shapes = pd.read_csv("data_preprocessing/processed/sound_transit_shapes.csv")

    # 2. Combine and drop duplicates
    all_stops = pd.concat([king_stops, sound_stops]).drop_duplicates()
    all_trips = pd.concat([king_trips, sound_trips]).drop_duplicates()
    all_stop_times = pd.concat([king_stop_times, sound_stop_times]).drop_duplicates()
    all_shapes = pd.concat([king_shapes, sound_shapes]).drop_duplicates()

    # 3. Save combined files
    all_stops.to_csv("data_preprocessing/processed/all_stops.csv", index=False)
    all_trips.to_csv("data_preprocessing/processed/all_trips.csv", index=False)
    all_stop_times.to_csv("data_preprocessing/processed/all_stop_times.csv", index=False)
    all_shapes.to_csv("data_preprocessing/processed/all_shapes.csv", index=False)

    print("✅ All transit systems (including shapes) combined successfully.")

if __name__ == "__main__":
    combine_transit()
