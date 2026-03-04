import os
import pandas as pd
from pantry_map.utilities.utility import lat_lon_to_mercator, color_from_id
from pantry_map.config import BASE_DIR

def get_transit_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw", "shapes.txt")
    transit_df = pd.read_csv(data_path)
    transit_df["x"], transit_df["y"] = lat_lon_to_mercator(
        transit_df["shape_pt_lat"].values,
        transit_df["shape_pt_lon"].values
    )
    grouped_df = transit_df.groupby("shape_id").agg({"x": list, "y": list}).reset_index()
    grouped_df['color'] = grouped_df['shape_id'].apply(color_from_id)
    return grouped_df

def get_foodbank_df():
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw",
                             "Emergency_Food_and_Meals_Seattle_and_King_County_20260222.csv")
    foodbank_df = pd.read_csv(data_path)
    foodbank_df["x"], foodbank_df["y"] = lat_lon_to_mercator(
        foodbank_df["Latitude"].values,
        foodbank_df["Longitude"].values
    )
    return foodbank_df
