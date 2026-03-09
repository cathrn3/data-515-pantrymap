import pandas as pd

# Load datasets
trips = pd.read_csv("data_preprocessing/processed/all_trips.csv")
stop_times = pd.read_csv("data_preprocessing/processed/all_stop_times.csv")
stops = pd.read_csv("data_preprocessing/processed/all_stops.csv")

# Join trips with stop_times
trip_stop_times = pd.merge(stop_times, trips, on="trip_id", how="left")

# Join the result with stops
final_data = pd.merge(trip_stop_times, stops, on="stop_id", how="left")

# Check result
print(final_data.head())

# Save if needed
final_data.to_csv("joined_transit_data.csv", index=False)