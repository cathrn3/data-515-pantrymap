"""Filter management for PantryMap using actual Seattle data columns."""

import pandas as pd
import numpy as np
from datetime import datetime


class FilterManager:
    """Manages filtering for Seattle food bank data."""
    
    def __init__(self, data):
        """
        Initialize with food bank DataFrame.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Food bank data with Seattle Open Data columns
        """
        self.original_data = data.copy()
        self.original_data.columns = self.original_data.columns.str.lower().str.replace(' ', '_').str.replace('/', '_')
        self.filtered_data = data.copy()
        self._user_location = None
        
        # Clean data on initialization
        self._clean_data()
    
    def _clean_data(self):
        """Remove entries with missing coordinates."""
        # Remove rows without latitude or longitude
        self.original_data = self.original_data.dropna(subset=['latitude', 'longitude'])
        self.filtered_data = self.original_data.copy()
    
    def set_user_location(self, lat, lng):
        """
        Set user location and calculate distances to all food banks.
        
        Parameters:
        -----------
        lat : float
            User latitude
        lng : float
            User longitude
        """
        self._user_location = (lat, lng)
        self._calculate_distances()
        return self


    def _calculate_distances(self):
        """Calculate haversine distance using vectorized operations."""
        if self._user_location is None:
           return
    
        user_lat, user_lng = self._user_location
        R = 3959  # Earth radius in miles
    
        # Vectorized calculation
        lat1, lon1 = np.radians(user_lat), np.radians(user_lng)
        lat2 = np.radians(self.filtered_data['latitude'].values)
        lon2 = np.radians(self.filtered_data['longitude'].values)
    
        dlat = lat2 - lat1
        dlon = lon2 - lon1
    
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
    
        self.filtered_data['distance'] = R * c
        self.filtered_data = self.filtered_data.sort_values('distance')
        
        user_lat, user_lng = self._user_location
        
        def haversine(row):
            """Calculate distance in miles using haversine formula."""
            R = 3959  # Earth radius in miles
            
            # Convert to radians
            lat1, lon1 = np.radians([user_lat, user_lng])
            lat2, lon2 = np.radians([row['latitude'], row['longitude']])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            
            return R * c
        
        self.filtered_data['distance'] = self.filtered_data.apply(haversine, axis=1)
        
        # Sort by distance by default
        self.filtered_data = self.filtered_data.sort_values('distance')
    
    def filter_by_distance(self, max_distance):
        """
        Filter by maximum distance.
        
        Parameters:
        -----------
        max_distance : float
            Maximum distance in miles
        """
        if 'distance' not in self.filtered_data.columns:
            return self
        
        if max_distance and max_distance > 0:
            self.filtered_data = self.filtered_data[
                self.filtered_data['distance'] <= max_distance
            ]
        
        return self
    
    def filter_by_type(self, resource_types):
        """
        Filter by food resource type.
        
        Parameters:
        -----------
        resource_types : list
            List like ["Food Bank", "Meal", "Food Bank & Meal"]
        """
        if not resource_types or len(resource_types) == 0:
            return self
        
        if 'food_resource_type' in self.filtered_data.columns:
            self.filtered_data = self.filtered_data[
                self.filtered_data['food_resource_type'].isin(resource_types)
            ]
        
        return self
    
    def filter_by_status(self, open_only=True):
        """
        Filter by operational status.
        
        Parameters:
        -----------
        open_only : bool
            If True, show only open locations
        """
        if open_only and 'operational_status' in self.filtered_data.columns:
            self.filtered_data = self.filtered_data[
                self.filtered_data['operational_status'].str.strip().str.lower() == 'open'
            ]
        
        return self
    
    def filter_by_eligibility(self, target_groups):
        """
        Filter by who they serve.
        
        Parameters:
        -----------
        target_groups : list
            List like ["General Public", "Seniors", "Youth and Young Adults"]
        """
        if not target_groups or len(target_groups) == 0:
            return self
        
        if 'who_they_serve' in self.filtered_data.columns:
            # Use case-insensitive partial matching
            def matches_group(who_served):
                if pd.isna(who_served):
                    return False
                who_served_lower = str(who_served).lower()
                return any(group.lower() in who_served_lower for group in target_groups)
            
            self.filtered_data = self.filtered_data[
                self.filtered_data['who_they_serve'].apply(matches_group)
            ]
        
        return self

    def filter_by_days(self, selected_days):
        """
        Filter by days of operation.
        
        Parameters:
        -----------
        selected_days : list
            List of days like ["Monday", "Tuesday", "Wednesday"]
        """
        if not selected_days or len(selected_days) == 0:
            return self
        
        if 'days_hours' in self.filtered_data.columns:
            day_patterns = {
                'Monday': ['monday', 'mon'],
                'Tuesday': ['tuesday', 'tues', 'tue'],
                'Wednesday': ['wednesday', 'wed'],
                'Thursday': ['thursday', 'thurs', 'thu'],
                'Friday': ['friday', 'fri'],
                'Saturday': ['saturday', 'sat'],
                'Sunday': ['sunday', 'sun']
            }
        
            def open_on_days(days_hours_text):
                if pd.isna(days_hours_text):
                    return False
            
                days_text = str(days_hours_text).lower()
                return any(
                    any(pattern in days_text for pattern in day_patterns.get(day, []))
                    for day in selected_days
                )
        
        self.filtered_data = self.filtered_data[
            self.filtered_data['days_hours'].apply(open_on_days)
        ]
    
        return self
    
    def filter_by_search(self, search_text):
        """
        Search in agency name, location, or address.
        
        Parameters:
        -----------
        search_text : str
            Search query
        """
        if not search_text or search_text.strip() == "":
            return self
        
        search_lower = search_text.lower()
        
        # Search across multiple fields
        mask = (
            self.filtered_data['agency'].str.lower().str.contains(search_lower, na=False) |
            self.filtered_data['location'].str.lower().str.contains(search_lower, na=False) |
            self.filtered_data['address'].str.lower().str.contains(search_lower, na=False)
        )
        
        self.filtered_data = self.filtered_data[mask]
        
        return self
    
    def reset(self):
        """Reset all filters to original data."""
        self.filtered_data = self.original_data.copy()
        
        # Recalculate distances if user location is set
        if self._user_location:
            self._calculate_distances()
        
        return self
    
    def get_data(self):
        """Return filtered DataFrame."""
        return self.filtered_data
    
    def get_count(self):
        """Return number of filtered results."""
        return len(self.filtered_data)
    
    def get_summary(self):
        """Get summary of filtering results."""
        return {
            'total_results': len(self.filtered_data),
            'original_count': len(self.original_data),
            'filtered_out': len(self.original_data) - len(self.filtered_data)
        }
