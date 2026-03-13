"""
Filtering logic for PantryMap data.

This module provides functions to create masks for filtering food bank data
based on user selections.
"""

import numpy as np

def get_foodbank_mask(foodbank_df, resource_types):
    """
    Create a boolean mask for filtering the food bank dataframe.

    Args:
        foodbank_df (pd.DataFrame): The dataframe to filter.
        resource_types (MultiSelect): The Bokeh MultiSelect widget containing selected types.

    Returns:
        np.array: A boolean array mask.
    """
    foodbank_mask = np.ones(len(foodbank_df), dtype=bool)
    foodbank_mask &= foodbank_df["Food Resource Type"].isin(resource_types.value)
    return foodbank_mask
