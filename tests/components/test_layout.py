"""Tests for layout components: HTML formatters, widget creators, and helpers."""
import unittest
from unittest.mock import patch
import datetime as dt

import pandas as pd
from bokeh.plotting import figure

from pantry_map.components.layout import (
    is_open_today,
    format_nearby_foodbanks,
    format_route_display,
    create_filter_bar,
    create_search_bar,
    create_nearby_panel,
    create_layout,
    create_sidebar,
    format_foodbank_list,
    _normalize_hex_color,
    _website_html,
    _status_badge,
)


# pylint: disable=protected-access


class TestIsOpenToday(unittest.TestCase):
    """Tests for the is_open_today helper."""

    def test_missing_data_returns_none(self):
        """None and empty string should return None."""
        self.assertIsNone(is_open_today(None))
        self.assertIsNone(is_open_today(""))

    @patch("pantry_map.components.layout.datetime")
    def test_daily(self, mock_dt):
        """'Daily' keyword should always return True."""
        mock_dt.now.return_value = dt.datetime(2026, 3, 18)  # Wednesday
        self.assertTrue(is_open_today("Daily 9am-5pm"))

    @patch("pantry_map.components.layout.datetime")
    def test_weekday_range(self, mock_dt):
        """Monday-Friday ranges should match weekdays, not weekends."""
        mock_dt.now.return_value = dt.datetime(2026, 3, 18)  # Wednesday
        self.assertTrue(is_open_today("Monday-Friday 9am"))
        self.assertTrue(is_open_today("Mon-Fri 9am"))
        mock_dt.now.return_value = dt.datetime(2026, 3, 21)  # Saturday
        self.assertFalse(is_open_today("Monday-Friday 9am"))

    @patch("pantry_map.components.layout.datetime")
    def test_specific_day(self, mock_dt):
        """Exact day name should match or not match."""
        mock_dt.now.return_value = dt.datetime(2026, 3, 16)  # Monday
        self.assertTrue(is_open_today("Monday 10am-2pm"))
        self.assertFalse(is_open_today("Wednesday 10am-2pm"))

    @patch("pantry_map.components.layout.datetime")
    def test_weekday_range_on_weekend_with_no_specific_day(self, mock_dt):
        """Mon-Fri on Saturday, with no Saturday mention, returns False."""
        mock_dt.now.return_value = dt.datetime(2026, 3, 21)  # Saturday
        self.assertFalse(is_open_today("Mon - Fri 8am-4pm"))


class TestNormalizeHexColor(unittest.TestCase):
    """Tests for _normalize_hex_color."""

    def test_valid_and_invalid(self):
        """Valid hex passes through lowercased; invalid returns default."""
        self.assertEqual(_normalize_hex_color("#A1B2C3"), "#a1b2c3")
        self.assertEqual(_normalize_hex_color("#abc"), "#abc")
        self.assertEqual(_normalize_hex_color(None), "#374151")
        self.assertEqual(_normalize_hex_color(""), "#374151")
        self.assertEqual(_normalize_hex_color("not-a-color"), "#374151")


class TestFormatNearbyFoodbanks(unittest.TestCase):
    """Tests for format_nearby_foodbanks HTML card generation."""

    def test_empty_inputs(self):
        """None and empty DataFrame both produce 'No matching' message."""
        self.assertIn("No matching", format_nearby_foodbanks(None))
        self.assertIn("No matching", format_nearby_foodbanks(pd.DataFrame()))

    def test_with_data(self):
        """Row data should appear in the HTML output."""
        df = pd.DataFrame({
            "Agency": ["Test Bank"],
            "Location": ["Downtown"],
            "Address": ["123 Main St"],
            "Phone Number": [None],
            "Food Resource Type": ["Food Bank"],
            "Website": ["https://example.com"],
            "Days/Hours": [None],
        })
        result = format_nearby_foodbanks(df)
        self.assertIn("Test Bank", result)
        self.assertIn("123 Main St", result)
        self.assertIn("Not available", result)  # None phone
        self.assertIn("Visit website", result)

    def test_with_distance_column(self):
        """Distance column should produce 'miles away' text."""
        df = pd.DataFrame({
            "Agency": ["A"],
            "Location": [""],
            "Address": [""],
            "Phone Number": ["555-1234"],
            "Food Resource Type": ["Meal"],
            "Website": [None],
            "Days/Hours": [None],
            "distance": [2.5],
        })
        result = format_nearby_foodbanks(df)
        self.assertIn("miles away", result)
        self.assertIn("555-1234", result)


class TestFormatRouteDisplay(unittest.TestCase):
    """Tests for format_route_display chip timeline."""

    def test_empty_legs(self):
        """Empty legs list should return empty string."""
        self.assertEqual(format_route_display([], 10, "Bank"), "")

    def test_walk_and_bus(self):
        """Walk + bus + walk should produce Walk, bus name, and Arrive chips."""
        legs = [
            {"type": "walk"},
            {"type": "bus", "short_name": "44", "color": "#ff0000"},
            {"type": "walk"},
        ]
        result = format_route_display(legs, 25, "Food Bank A")
        self.assertIn("Walk", result)
        self.assertIn("44", result)
        self.assertIn("Arrive", result)
        self.assertIn("25 min", result)

    def test_time_formatting(self):
        """75 min -> '1 hr 15 min'; 120 min -> '2 hr' (no '0 min')."""
        legs = [{"type": "walk"}]
        self.assertIn("1 hr 15 min", format_route_display(legs, 75, "X"))
        self.assertIn("2 hr", format_route_display(legs, 120, "X"))
        self.assertNotIn("0 min", format_route_display(legs, 120, "X"))


class TestWebsiteAndStatusBadge(unittest.TestCase):
    """Tests for _website_html and _status_badge helpers."""

    def test_website_html(self):
        """Valid URL produces link; None/nan produce empty string."""
        self.assertIn("href=", _website_html({"Website": "https://example.com"}))
        self.assertEqual("", _website_html({"Website": None}))
        self.assertEqual("", _website_html({"Website": "nan"}))
        self.assertEqual("", _website_html({}))

    @patch("pantry_map.components.layout.is_open_today")
    def test_status_badge(self, mock_open):
        """Open/closed/None produce green/red/empty badges."""
        mock_open.return_value = True
        self.assertIn("Open Today", _status_badge({"Days/Hours": "x"}))
        mock_open.return_value = False
        self.assertIn("Closed Today", _status_badge({"Days/Hours": "x"}))
        mock_open.return_value = None
        self.assertEqual("", _status_badge({"Days/Hours": None}))


class TestWidgetCreators(unittest.TestCase):
    """Tests for widget factory functions."""

    def test_create_filter_bar(self):
        """Filter bar should return expected widget keys."""
        _, widgets = create_filter_bar()
        self.assertIn("resource_type_selector", widgets)
        self.assertIn("eligibility_group", widgets)
        self.assertIn("day_group", widgets)

    def test_create_search_bar(self):
        """Search bar should return all expected widget keys."""
        _, widgets = create_search_bar()
        for key in ("address_input", "search_button", "clear_button",
                     "distance_slider", "results_div"):
            self.assertIn(key, widgets)

    def test_create_nearby_panel(self):
        """Nearby panel should return a location_list widget."""
        _, widgets = create_nearby_panel()
        self.assertIn("location_list", widgets)

    def test_create_header_and_layout(self):
        """Full layout assembly should succeed without error."""
        fig = figure(width=100, height=100)
        filter_bar, _ = create_filter_bar()
        search_bar, _ = create_search_bar()
        nearby, _ = create_nearby_panel()
        result = create_layout(fig, filter_bar, search_bar, nearby)
        self.assertIsNotNone(result)

    def test_deprecated_create_sidebar(self):
        """Deprecated create_sidebar should return empty dict."""
        _, widgets = create_sidebar()
        self.assertEqual(widgets, {})

    def test_format_foodbank_list_alias(self):
        """Backward-compatible alias should delegate correctly."""
        self.assertIn("No matching", format_foodbank_list(None))


if __name__ == "__main__":
    unittest.main()
