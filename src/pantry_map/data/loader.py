import os
import pandas as pd
from pantry_map.utilities.utility import lat_lon_to_mercator, color_from_id
from pantry_map.config import BASE_DIR

def get_transit_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw", "shapes.txt")
    df = pd.read_csv(data_path)
    df['x'], df['y'] = zip(*[lat_lon_to_mercator(lat, lon) for lat, lon in zip(df['shape_pt_lat'], df['shape_pt_lon'])])
    grouped_df = df.groupby("shape_id").agg({"x": list, "y": list}).reset_index()
    grouped_df['color'] = grouped_df['shape_id'].apply(color_from_id)
    return grouped_df

def get_foodbank_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw", "Emergency_Food_and_Meals_Seattle_and_King_County_20260222.csv")
    df = pd.read_csv(data_path)
    df['x'], df['y'] = zip(*[lat_lon_to_mercator(lat, lon) for lat, lon in zip(df['Latitude'], df['Longitude'])])
    return df