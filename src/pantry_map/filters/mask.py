import numpy as np

def get_foodbank_mask(foodbank_df, resource_types):
    foodbank_mask = np.ones(len(foodbank_df), dtype=bool)
    foodbank_mask &= foodbank_df["Food Resource Type"].isin(resource_types.value)
    return foodbank_mask