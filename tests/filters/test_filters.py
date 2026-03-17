"""Tests for food bank filtering masks."""
import datetime as dt
import unittest
from unittest.mock import patch

import pandas as pd

from pantry_map.filters.mask import get_foodbank_mask


class TestFoodbankFilters(unittest.TestCase):
    """Tests for foodbank filters."""
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "Food Resource Type": ["Food Bank", "Meal", "Food Bank & Meal", "Meal"],
                "Operational Status": ["Open", "Closed", "Open", "Open"],
                "Who They Serve": [
                    "General Public",
                    "Older Adults 60+ and Eligible Participants",
                    "Youth and General Public",
                    "General Public",
                ],
                "Days/Hours": [
                    "Monday, Wednesday",
                    "Tuesday",
                    "Sunday",
                    "Friday, Saturday",
                ],
                "Latitude": [47.60, 47.61, 47.65, 47.90],
                "Longitude": [-122.33, -122.34, -122.30, -122.20],
            }
        )

    def test_resource_type_food_bank_excludes_combo(self):
        """Test that filtering by 'Food Bank' excludes combination resource types."""
        mask = get_foodbank_mask(self.df, resource_type="Food Bank")
        self.assertEqual(mask.tolist(), [True, False, False, False])

    def test_resource_type_meal_excludes_combo(self):
        """Test function."""
        mask = get_foodbank_mask(self.df, resource_type="Meal")
        self.assertEqual(mask.tolist(), [False, True, False, True])

    def test_open_only_filter(self):
        """Test function."""
        mask = get_foodbank_mask(self.df, open_only=True, current_day="Monday")
        self.assertEqual(mask.tolist(), [True, False, False, False])

    def test_open_only_excludes_closed_today_locations(self):
        """Test function."""
        mask = get_foodbank_mask(self.df, open_only=True, current_day="Sunday")
        self.assertEqual(mask.tolist(), [False, False, True, False])

    def test_eligibility_filter_seniors(self):
        """Test function."""
        mask = get_foodbank_mask(self.df, selected_eligibility=["Seniors"])
        self.assertEqual(mask.tolist(), [False, True, False, False])

    def test_empty_eligibility_means_no_filtering(self):
        """Test function."""
        # Empty eligibility selection should not filter out any rows
        mask = get_foodbank_mask(self.df, selected_eligibility=[])
        self.assertEqual(mask.tolist(), [True, True, True, True])

    def test_day_of_week_filter(self):
        """Test function."""
        mask = get_foodbank_mask(self.df, selected_days=["Sunday"])
        self.assertEqual(mask.tolist(), [False, False, True, False])

    def test_empty_days_means_no_filtering(self):
        """Test function."""
        # Empty day selection should not filter out any rows
        mask = get_foodbank_mask(self.df, selected_days=[])
        self.assertEqual(mask.tolist(), [True, True, True, True])

    def test_empty_eligibility_and_days_with_open_only(self):
        """Test function."""
        # Empty eligibility + days: only open_only should apply
        mask = get_foodbank_mask(
            self.df,
            open_only=True,
            selected_eligibility=[],
            selected_days=[],
            current_day="Sunday",
        )
        self.assertEqual(mask.tolist(), [False, False, True, False])

    def test_distance_filter_with_user_location(self):
        """Test function."""
        # Roughly near row 0/1/2, far from row 3
        mask = get_foodbank_mask(
            self.df,
            user_lat=47.60,
            user_lon=-122.33,
            max_distance_miles=10,
        )
        self.assertEqual(mask.tolist(), [True, True, True, False])

    def test_combined_filters(self):
        """Test function."""
        mask = get_foodbank_mask(
            self.df,
            resource_type="Meal",
            open_only=True,
            selected_eligibility=["General Public"],
            selected_days=["Friday"],
            current_day="Friday",
        )
        self.assertEqual(mask.tolist(), [False, False, False, True])

    def test_open_only_auto_detects_current_day(self):
        """open_only=True with current_day=None should use datetime.now()."""
        fake_now = dt.datetime(2026, 3, 18, 12, 0)  # Wednesday
        with patch("pantry_map.filters.mask.datetime") as mock_dt:
            mock_dt.now.return_value = fake_now
            mask = get_foodbank_mask(self.df, open_only=True, current_day=None)
        self.assertTrue(mask[0])   # row 0: Open + "Monday, Wednesday"
        self.assertFalse(mask[1])  # row 1: Closed

    def test_eligibility_youth(self):
        """'Youth' filter matches rows with youth/children/teen/student."""
        df = pd.DataFrame({
            "Food Resource Type": ["Food Bank", "Food Bank"],
            "Operational Status": ["Open", "Open"],
            "Who They Serve": ["youth programs", "General Public"],
            "Days/Hours": ["Monday", "Monday"],
            "Latitude": [47.6, 47.6],
            "Longitude": [-122.3, -122.3],
        })
        mask = get_foodbank_mask(df, selected_eligibility=["Youth"])
        self.assertTrue(mask[0])
        self.assertFalse(mask[1])

    def test_distance_mask_with_bad_coords(self):
        """Rows with non-numeric or NaN coords should be excluded by distance filter."""
        df = pd.DataFrame({
            "Food Resource Type": ["Food Bank"] * 4,
            "Operational Status": ["Open"] * 4,
            "Who They Serve": ["General Public"] * 4,
            "Days/Hours": ["Monday"] * 4,
            "Latitude": [47.60, "bad", None, float("nan")],
            "Longitude": [-122.33, -122.33, -122.33, -122.33],
        })
        mask = get_foodbank_mask(df, user_lat=47.60, user_lon=-122.33, max_distance_miles=10)
        self.assertTrue(mask[0])
        self.assertFalse(mask[1])   # "bad" string
        self.assertFalse(mask[2])   # None
        self.assertFalse(mask[3])   # NaN (passes float() but fails isfinite)


if __name__ == "__main__":
    unittest.main()
