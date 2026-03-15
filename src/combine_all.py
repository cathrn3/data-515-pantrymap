"""
Script to combine transit datasets including trips, stop_times, and stops.

This script merges various stages of processed transit data into a single,
comprehensive dataframe for further analysis.
"""

import pandas as pd

def combine_transit_data():
    """
    Merge the processed trips, stop_times, and stops data into one CSV.
    """
    # Load datasets
    trips = pd.read_csv("data_preprocessing/processed/all_trips.csv")
    stop_times = pd.read_csv("data_preprocessing/processed/all_stop_times.csv")
    stops = pd.read_csv("data_preprocessing/processed/all_stops.csv")

    # Join trips with stop_times
    stop_times['trip_id'] = stop_times['trip_id'].astype(str)
    trips['trip_id'] = trips['trip_id'].astype(str)
    trip_stop_times = pd.merge(stop_times, trips, on="trip_id", how="left")

    # Join the result with stops
    trip_stop_times['stop_id'] = trip_stop_times['stop_id'].astype(str)
    stops['stop_id'] = stops['stop_id'].astype(str)
    final_data = pd.merge(trip_stop_times, stops, on="stop_id", how="left")

    # Print check
    print(final_data.head())

    # Save to CSV
    final_data.to_csv("joined_transit_data.csv", index=False)

if __name__ == "__main__":
    combine_transit_data()
