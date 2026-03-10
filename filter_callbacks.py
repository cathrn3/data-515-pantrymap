"""Callback functions for filter interactions."""

from bokeh.models import ColumnDataSource


class FilterCallbacks:
    """Manages all filter callbacks."""
    
    def __init__(self, filter_manager, widgets, data_source):
        """
        Initialize callback handler.
        
        Parameters:
        -----------
        filter_manager : FilterManager
            Instance of FilterManager
        widgets : FilterWidgets
            Instance of FilterWidgets
        data_source : ColumnDataSource
            Bokeh data source connected to map
        """
        self.filter_manager = filter_manager
        self.widgets = widgets
        self.data_source = data_source
        self.total_count = filter_manager.get_count()
    
    def attach_all_callbacks(self):
        """Attach all callbacks to widgets."""
        
        # Distance slider
        self.widgets.distance_slider.on_change('value', self._on_filter_change)
        
        # Type selector
        self.widgets.type_select.on_change('value', self._on_filter_change)
        
        # Eligibility selector
        self.widgets.eligibility_select.on_change('value', self._on_filter_change)
        
        # Day checkboxes
        self.widgets.day_checkboxes.on_change('active', self._on_filter_change)
        
        # Open only toggle
        self.widgets.open_only_toggle.on_change('active', self._on_filter_change)
        
        # Search input
        self.widgets.search_input.on_change('value', self._on_filter_change)
        
        # Reset button
        self.widgets.reset_button.on_click(self._on_reset)
        
        print(" All callbacks attached successfully")
    
    def _apply_all_filters(self):
        """Apply all active filters in sequence."""
        
        # Start fresh
        self.filter_manager.reset()
        
        # 1. Distance filter
        max_distance = self.widgets.distance_slider.value
        self.filter_manager.filter_by_distance(max_distance)
        
        # 2. Type filter
        selected_types = self.widgets.type_select.value
        if selected_types:
            self.filter_manager.filter_by_type(selected_types)
        
        # 3. Status filter (open only)
        open_only = self.widgets.open_only_toggle.active
        self.filter_manager.filter_by_status(open_only)
        
        # 4. Eligibility filter
        selected_eligibility = self.widgets.eligibility_select.value
        if selected_eligibility:
            self.filter_manager.filter_by_eligibility(selected_eligibility)
        
        # 5. Day of week filter
        day_labels = self.widgets.day_checkboxes.labels
        active_indices = self.widgets.day_checkboxes.active
        selected_days = [day_labels[i] for i in active_indices]
        if selected_days:
            self.filter_manager.filter_by_days(selected_days)
        
        # 6. Search filter
        search_text = self.widgets.search_input.value
        if search_text and search_text.strip():
            self.filter_manager.filter_by_search(search_text)
        
        # Update display
        self._update_map()
        self._update_results_count()


    def _update_map(self):
        """Update map data source with filtered results."""
        filtered_df = self.filter_manager.get_data().copy()

        # Recalculate Mercator coordinates for filtered data
        if len(filtered_df) > 0 and 'latitude' in filtered_df.columns:
            from interated_main import lat_lng_to_mercator
            mercator_coords = filtered_df.apply(
                lambda row: lat_lng_to_mercator(row['latitude'], row['longitude']),
                axis=1
            )
            filtered_df['mercator_x'] = [coord[0] for coord in mercator_coords]
            filtered_df['mercator_y'] = [coord[1] for coord in mercator_coords]
        
        # Convert DataFrame to dictionary for ColumnDataSource
        new_data = {}
        for col in filtered_df.columns:
            new_data[col] = filtered_df[col].tolist()
        
        # Update the data source (this triggers map update)
        self.data_source.data = new_data
    
    def _update_results_count(self):
        """Update results counter display."""
        filtered_count = self.filter_manager.get_count()
        self.widgets.update_results_display(filtered_count, self.total_count)
    
    # Callback functions
    def _on_filter_change(self, attr, old, new):
        """Called when any filter widget changes."""
        self._apply_all_filters()
    
    def _on_reset(self):
        """Called when reset button is clicked."""
        # Clear all widget selections
        self.widgets.type_select.value = []
        self.widgets.eligibility_select.value = []
        self.widgets.day_checkboxes.active = []
        self.widgets.open_only_toggle.active = True
        self.widgets.search_input.value = ""
        self.widgets.distance_slider.value = 10
        
        # Apply filters (now cleared)
        self._apply_all_filters()
    
    def initialize_display(self):
        """Initialize the display on first load."""
        self._apply_all_filters()
