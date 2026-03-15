"""
Data loading utilities for the PantryMap application.

This module provides functions to load and preprocess transit and food bank
data for the interactive map and dashboard.
"""

import os
import pandas as pd
from pantry_map.config import BASE_DIR

def get_shapes_df():
    """
    Load and process transit shapes data.

    Returns:
        tuple: (transit_df, grouped_df) where grouped_df contains routes grouped by
               route_id and direction_id with their colors.
    """
    data_path = os.path.join(BASE_DIR, "pantry_map", "data", "raw", "all_shapes_labeled.csv")
    transit_df = pd.read_csv(data_path)
    grouped_df = transit_df.groupby(["route_id", "direction_id"]).agg({"x": list, "y": list, "color": "first"}).reset_index()
    return transit_df, grouped_df

def get_foodbank_df():
    """
    Load and process food bank data (location and contact info).

    Returns:
        pd.DataFrame: Dataframe containing food bank locations and mapping coordinates.
    """
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