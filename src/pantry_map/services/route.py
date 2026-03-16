"""
This module handles finding the estimated optimal route between a user's location
and a food bank via public transportation
"""

import logging
from itertools import groupby

import networkx as nx
import numpy as np
from sklearn.neighbors import BallTree


class CalculateRoute:  # pylint: disable=too-many-instance-attributes
    """
    Find the shortest path via public transportation between a user and a selected food bank
    using Dijkstra's algorithm.
    Food banks and public transit stops are reachable by the user if they are within 1 mile.
    The estimated in-vehicle time along a route is calculated from the schedule information
    in the transit dataset.
    The estimated walking time to a node is calculated using the distance and an assumed
    walking speed.
    The estimated time taken to make a bus transfer is taken from the transfer data
    (e.g., ``transfers_df['estimated_time']``) rather than being a fixed constant.
    """
    USER_ALLOWED_DIST = 1 # Allow 1 mile between user and nodes
    WALKING_SPEED = 2 # Assumed walking speed at 2 MPH

    def __init__(self, food_bank_df, transit_df, transfers_df):
        self._route_lookup = {}
        self.user_location = None
        # Filter out food banks without valid coordinates so that indices from the
        # BallTree correspond directly to rows in self.food_bank_df.
        self.food_bank_df = (
            food_bank_df.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)
        )
        self.transit_df = transit_df
        self.transfers_df = transfers_df
        self.graph = self._initialize_graph()

        # Use a filtered transit DataFrame for spatial queries so BallTree indices align
        self.transit_df_nonnull = (
            self.transit_df.dropna(subset=['stop_lat', 'stop_lon']).reset_index(drop=True)
        )
        self.transit_coords = np.radians(self.transit_df_nonnull[['stop_lat', 'stop_lon']])
        self.transit_tree = BallTree(self.transit_coords, metric='haversine')

        # Build the BallTree from the same filtered DataFrame used throughout the class,
        # ensuring that returned indices can be safely applied with .iloc on self.food_bank_df.
        self.food_bank_coords = np.radians(self.food_bank_df[['Latitude','Longitude']])
        self.food_bank_tree = BallTree(self.food_bank_coords, metric='haversine')

    def _initialize_graph(self):
        """
        Connect bus stops within each route and connect all available transfers between routes
        """
        graph = nx.DiGraph() # Bus routes are directional
        df_edges = self.transit_df[self.transit_df["next_stop"].notna()]
        edge_list = list(zip(
            df_edges["unique_key"],
            df_edges["next_stop"],
            df_edges["estimated_travel_time_minutes_between_stops"]
        ))
        graph.add_weighted_edges_from(edge_list)
        transfer_list = list(zip(
            self.transfers_df["source_node"],
            self.transfers_df["nearby_node"],
            self.transfers_df["estimated_time"]
        ))
        graph.add_weighted_edges_from(transfer_list)
        return graph

    def set_user_location(self, user_location: tuple | None):
        """Set the user's current location and update their node in the graph."""
        self.user_location = user_location  # lat, lon coordinates
        if user_location is not None:
            self._add_user_location_to_graph()

    def get_user_location(self):
        """Return the user's current location as a (lat, lon) tuple, or None."""
        return self.user_location

    def _get_nearby_nodes(self, tree, source_coords: tuple, radius: int):
        """Get nodes in the tree within the given radius to the source coordinates"""
        lat, lon = source_coords
        coords = [[np.radians(lat), np.radians(lon)]]
        allowed_radius = radius / 3959

        indices, dist = tree.query_radius(coords, r=allowed_radius, return_distance=True)
        return indices[0], dist[0] * 3959

    def _remove_old_user_location_from_graph(self):
        """Remove old address on updates"""
        if "USER" in self.graph:
            self.graph.remove_node("USER")

    def _add_user_location_to_graph(self):
        """
        Modifies the graph to include the user as a node.
        Users are connected to any nodes within a mile.
        """
        self._remove_old_user_location_from_graph()
        transit_idx, transit_dist = self._get_nearby_nodes(
            self.transit_tree, self.user_location, self.USER_ALLOWED_DIST
        )
        food_bank_idx, food_bank_dist = self._get_nearby_nodes(
            self.food_bank_tree, self.user_location, self.USER_ALLOWED_DIST
        )

        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            stop_key = self.transit_df['unique_key'].iloc[df_index]
            self.graph.add_edge("USER", stop_key, weight=estimated_time)
            self.graph.add_edge(stop_key, "USER", weight=estimated_time)

        for df_index, dist in zip(food_bank_idx, food_bank_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60  # in minutes
            bank_id = self.food_bank_df['bank_id'].iloc[df_index]
            self.graph.add_edge("USER", bank_id, weight=estimated_time)
            self.graph.add_edge(bank_id, "USER", weight=estimated_time)

    def _get_nearby_nodes_to_food_bank(self, food_bank_id: str):
        """Temporarily connect the given food bank to the graph, returning a copy."""
        food_bank = self.food_bank_df[self.food_bank_df['bank_id'] == food_bank_id]
        if food_bank.empty:
            # Explicitly handle unknown food bank IDs instead of raising IndexError
            raise ValueError(f"Unknown food bank id: {food_bank_id}")
        coords = tuple(food_bank[['Latitude', 'Longitude']].iloc[0])
        transit_idx, transit_dist = self._get_nearby_nodes(
            self.transit_tree, coords, self.USER_ALLOWED_DIST
        )

        new_graph = self.graph.copy()  # Safely copies graph for adding temp edges
        for df_index, dist in zip(transit_idx, transit_dist):
            estimated_time = (dist / self.WALKING_SPEED) * 60
            # Map BallTree indices back to the filtered transit_df_nonnull to avoid misalignment
            stop_id = self.transit_df_nonnull['unique_key'].iloc[df_index]
            new_graph.add_edge(food_bank_id, stop_id, weight=estimated_time)
            new_graph.add_edge(stop_id, food_bank_id, weight=estimated_time)
        return new_graph

    def _build_legs(self, route):  # pylint: disable=too-many-branches
        """Reconstruct leg sequence from a node path returned by Dijkstra.

        Each edge is classified as "walk" (USER node or food bank destination)
        or a route short name (looked up via unique_key in transit_df).
        Consecutive edges with the same short name are merged into one bus leg.

        Args:
            route (list[str]): Ordered list of node IDs from USER to food bank.

        Returns:
            list[dict]: Leg dicts — {"type": "walk"} or
                        {"type": "bus", "short_name": str, "color": str}
        """
        food_bank_ids = set(self.food_bank_df["bank_id"].values)

        # Lazily build a lookup from unique_key -> {"route_short_name": ..., "color": ...}
        # to avoid repeated boolean indexing and to handle missing keys safely.
        if not hasattr(self, "_route_lookup"):
            try:
                self._route_lookup = (
                    self.transit_df
                    .set_index("unique_key")[["route_short_name", "color"]]
                    .to_dict("index")
                )
            except Exception:  # pylint: disable=broad-exception-caught
                # Fallback if transit_df is missing expected columns
                self._route_lookup = {}

        # Classify each edge as "walk" or a (short_name, info) tuple
        classified = []
        for node_a, node_b in zip(route, route[1:]):
            if (
                node_a == "USER"
                or node_b == "USER"
                or node_a in food_bank_ids
                or node_b in food_bank_ids
            ):
                classified.append(("walk", None))
            else:
                route_info = self._route_lookup.get(node_a)
                # If no route info is found, treat this edge as a walk/transfer leg
                if not route_info:
                    classified.append(("walk", None))
                else:
                    short_name = route_info.get("route_short_name")
                    if not short_name:
                        # Missing short name: fall back to walk to avoid breaking routing
                        classified.append(("walk", None))
                    else:
                        classified.append((short_name, route_info))

        # Group consecutive same-label edges into legs
        legs = []
        for short_name, group in groupby(classified, key=lambda x: x[0]): # pylint: disable=too-many-branches
            if short_name == "walk":
                legs.append({"type": "walk"})
            else:
                _, first_row = next(group)
                # Safely extract color; default to None if unavailable
                color = None
                if first_row is not None:
                    try:
                        color = (
                            first_row.get("color")
                            if hasattr(first_row, "get")
                            else first_row["color"]
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        color = None
                legs.append({
                    "type": "bus",
                    "short_name": short_name,
                    "color": color,
                })

        return legs

    def get_route_to_destination(self, food_bank_id: str):
        """Return the shortest path, estimated travel time, and leg list to the given food bank."""
        try:
            if self.user_location is None:
                return None, None, None
            new_graph = self._get_nearby_nodes_to_food_bank(food_bank_id)
            time, route = nx.single_source_dijkstra(
                new_graph, 'USER', food_bank_id, weight='weight'
            )
            legs = self._build_legs(route)
            return time, route, legs
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None, None, None
        except ValueError:
            # Handle unknown food bank IDs
            return None, None, None
        except Exception:  # pylint: disable=broad-exception-caught
            logging.exception(
                "Unexpected error occurred while finding route to food bank %s",
                food_bank_id,
            )
            return None, None, None
