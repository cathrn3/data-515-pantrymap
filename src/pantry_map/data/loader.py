import os
import pandas as pd
from pantry_map.config import BASE_DIR

def get_shapes_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw", "all_shapes_labeled.csv")
    transit_df = pd.read_csv(data_path)
    grouped_df = transit_df.groupby("route_id").agg({"x": list, "y": list}).reset_index()
    return grouped_df

def get_foodbank_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw",
                             "clean_food_resources.csv")
    foodbank_df = pd.read_csv(data_path)
    return foodbank_df

def get_transit_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw",
                             "transit.csv")
    df = pd.read_csv(data_path)
    return df

def get_transfers_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw",
                             "transfers.csv")
    df = pd.read_csv(data_path)
    return df