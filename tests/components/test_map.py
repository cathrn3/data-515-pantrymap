"""Tests for map components: figure creation, markers, routes, and clearing."""
import unittest

import pandas as pd
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter

from pantry_map.components.map import (
    create_map, add_markers, add_routes, update_route, clear_routes,
)


class TestCreateMap(unittest.TestCase):
    """Tests for create_map bounds computation."""

    def test_normal_data(self):
        """Valid data should produce a figure with data-derived ranges."""
        df = pd.DataFrame({
            "x": [-13620000, -13610000, -13600000, -13630000],
            "y": [6050000, 6060000, 6070000, 6055000],
        })
        fig = create_map(df)
        self.assertIsNotNone(fig)
        # Range should be derived from data, not defaults
        self.assertGreater(fig.x_range.start, -13650000)

    def test_empty_and_nan_fall_to_defaults(self):
        """Empty or all-NaN data should fall back to Seattle defaults."""
        empty_fig = create_map(pd.DataFrame({"x": [], "y": []}))
        self.assertAlmostEqual(empty_fig.x_range.start, -13650000)

        nan_fig = create_map(
            pd.DataFrame({"x": [float("nan")], "y": [float("nan")]})
        )
        self.assertAlmostEqual(nan_fig.x_range.start, -13650000)

    def test_single_point_degenerate_quantiles(self):
        """Single point: q_low == q_high and min == max, falls to defaults."""
        fig = create_map(pd.DataFrame({"x": [100.0], "y": [200.0]}))
        self.assertAlmostEqual(fig.x_range.start, -13650000)

    def test_two_points_uses_minmax_fallback(self):
        """Two points with degenerate quantiles use min/max + padding."""
        fig = create_map(
            pd.DataFrame({"x": [100.0, 200.0], "y": [300.0, 400.0]})
        )
        # Should use min/max path with padding, not defaults
        self.assertLess(fig.x_range.start, 100.0)
        self.assertGreater(fig.x_range.end, 200.0)


class TestMarkersAndRoutes(unittest.TestCase):
    """Tests for add_markers and add_routes."""

    def test_add_markers_and_routes(self):
        """Adding markers and routes should not raise."""
        df = pd.DataFrame({"x": [-13620000], "y": [6050000]})
        fig = create_map(df)
        source = ColumnDataSource({"x": [1], "y": [2]})
        shapes_source = ColumnDataSource(
            {"x": [[1, 2]], "y": [[3, 4]], "color": ["red"]}
        )
        route_source = ColumnDataSource(
            {"xs": [], "ys": [], "color": []}
        )
        view = CDSView(filter=BooleanFilter([True]))
        renderer = add_markers(fig, source, view=view)
        self.assertIsNotNone(renderer)
        add_routes(fig, shapes_source, route_source)


class TestUpdateAndClearRoute(unittest.TestCase):
    """Tests for update_route and clear_routes."""

    def setUp(self):
        """Create fresh ColumnDataSources for each test."""
        self.highlight = ColumnDataSource({"x": [], "y": []})
        self.route_src = ColumnDataSource(
            {"xs": [], "ys": [], "color": []}
        )
        self.foodbank_src = ColumnDataSource({"x": [1], "y": [2]})

    def test_update_route_with_valid_route(self):
        """Valid route should populate route_source and set highlight."""
        shapes_df = pd.DataFrame({
            "unique_key": ["s1", "s1", "s2", "s2"],
            "route_id": ["R1", "R1", "R1", "R1"],
            "x": [10, 20, 30, 40],
            "y": [11, 21, 31, 41],
            "color": ["#ff0000"] * 4,
        })
        update_route(
            route=["USER", "s1", "s2", "bank1"],
            foodbank_loc=(99, 88),
            source=shapes_df,
            foodbank_highlight_source=self.highlight,
            route_source=self.route_src,
        )
        self.assertEqual(self.highlight.data["x"], [99])
        self.assertTrue(len(self.route_src.data["xs"]) > 0)

    def test_update_route_none_clears(self):
        """None route should clear route_source but still set highlight."""
        update_route(
            None, (99, 88), pd.DataFrame(),
            self.highlight, self.route_src,
        )
        self.assertEqual(self.route_src.data["xs"], [])
        self.assertEqual(self.highlight.data["x"], [99])

    def test_clear_routes(self):
        """clear_routes should empty all sources and clear selection."""
        self.foodbank_src.selected.indices = [0]
        clear_routes(self.highlight, self.foodbank_src, self.route_src)
        self.assertEqual(self.highlight.data["x"], [])
        self.assertEqual(self.foodbank_src.selected.indices, [])
        self.assertEqual(self.route_src.data["xs"], [])


if __name__ == "__main__":
    unittest.main()
