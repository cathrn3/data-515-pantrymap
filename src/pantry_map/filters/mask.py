
from datetime import datetime
import numpy as np
from pantry_map.utilities.utility import calculate_distance


def _resource_type_mask(foodbank_df, resource_type):
    resource_series = foodbank_df["Food Resource Type"].fillna("").astype(str)

    if resource_type == "Food Bank":
        return resource_series.str.contains("Food Bank", case=False, regex=False)
    if resource_type == "Meal":
        return resource_series.str.contains("Meal", case=False, regex=False)
    return np.ones(len(foodbank_df), dtype=bool)


def _operational_status_mask(foodbank_df, open_only, current_day=None):
    if not open_only:
        return np.ones(len(foodbank_df), dtype=bool)

    if current_day is None:
        current_day = datetime.now().strftime("%A")

    status_mask = (
        foodbank_df["Operational Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("open")
    )

    available_today_mask = (
        foodbank_df["Days/Hours"]
        .fillna("")
        .astype(str)
        .str.contains(current_day, case=False, regex=False)
    )

    return status_mask & available_today_mask


def _eligibility_mask(foodbank_df, selected_eligibility):
    if not selected_eligibility:
        return np.ones(len(foodbank_df), dtype=bool)

    who_serve = foodbank_df["Who They Serve"].fillna("").astype(str)
    mask = np.zeros(len(foodbank_df), dtype=bool)

    for selection in selected_eligibility:
        if selection == "General Public":
            mask |= who_serve.str.contains("general public", case=False, regex=False)
        elif selection == "Seniors":
            mask |= who_serve.str.contains("older|senior|60\\+", case=False, regex=True)
        elif selection == "Youth":
            mask |= who_serve.str.contains("youth|children|teen|student", case=False, regex=True)

    return mask


def _day_mask(foodbank_df, selected_days):
    if not selected_days:
        return np.ones(len(foodbank_df), dtype=bool)

    days_text = foodbank_df["Days/Hours"].fillna("").astype(str)
    mask = np.zeros(len(foodbank_df), dtype=bool)
    for day in selected_days:
        mask |= days_text.str.contains(day, case=False, regex=False)
    return mask


def _distance_mask(foodbank_df, user_lat, user_lon, max_distance_miles):
    if user_lat is None or user_lon is None:
        return np.ones(len(foodbank_df), dtype=bool)

    def _within_distance(row):
        lat = row["Latitude"]
        lon = row["Longitude"]

        # Safely handle missing or non-numeric coordinates
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return False

        if not np.isfinite(lat) or not np.isfinite(lon):
            return False

        return calculate_distance(user_lat, user_lon, lat, lon) <= max_distance_miles

    return foodbank_df.apply(_within_distance, axis=1)


def get_foodbank_mask(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    foodbank_df,
    resource_type="Both",
    open_only=False,
    selected_eligibility=None,
    selected_days=None,
    user_lat=None,
    user_lon=None,
    max_distance_miles=25,
    current_day=None,
):
    """
    Create a boolean mask for filtering the food bank dataframe.

    Args:
        foodbank_df (pd.DataFrame): The dataframe to filter.
        resource_types (MultiSelect): The Bokeh MultiSelect widget containing selected types.

    Returns:
        np.array: A boolean array mask.
    """
    selected_eligibility = selected_eligibility or []
    selected_days = selected_days or []
    foodbank_mask = np.ones(len(foodbank_df), dtype=bool)
    foodbank_mask &= _resource_type_mask(foodbank_df, resource_type)
    foodbank_mask &= _operational_status_mask(foodbank_df, open_only, current_day)
    foodbank_mask &= _eligibility_mask(foodbank_df, selected_eligibility)
    foodbank_mask &= _day_mask(foodbank_df, selected_days)
    foodbank_mask &= _distance_mask(foodbank_df, user_lat, user_lon, max_distance_miles)
    return np.array(foodbank_mask, dtype=bool)
