"""Bokeh UI widgets for PantryMap filters."""

from bokeh.models import (
    Slider, MultiSelect, CheckboxGroup, 
    Toggle, Button, Div, TextInput
)
from bokeh.layouts import column


class FilterWidgets:
    """Creates all filter UI components."""
    
    def __init__(self):
        """Initialize all filter widgets."""
        
        # Distance slider
        self.distance_slider = Slider(
            start=1,
            end=25,
            value=10,
            step=0.5,
            title="Maximum Distance (miles)",
            width=280
        )
        
        # Food resource type (multi-select)
        self.type_select = MultiSelect(
            title="Food Resource Type",
            options=[
                ("Food Bank", "Food Bank"),
                ("Meal", "Meal Program"),
                ("Food Bank & Meal", "Food Bank & Meal")
            ],
            value=[],  # None selected by default
            width=280,
            size=3
        )
        
        # Who they serve (multi-select)
        self.eligibility_select = MultiSelect(
            title="Who They Serve",
            options=[],  # Will be populated from data
            value=[],
            width=280,
            size=4
        )
        
        # Day of week checkboxes
        self.day_checkboxes = CheckboxGroup(
            labels=[
                "Monday",
                "Tuesday", 
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ],
            active=[],  # None selected by default
            width=280
        )
        
        # Open locations only toggle
        self.open_only_toggle = Toggle(
            label="Open Locations Only",
            active=True,  # Default to showing only open locations
            button_type="success",
            width=280
        )
        
        # Search box
        self.search_input = TextInput(
            title="Search by Name or Address",
            placeholder="e.g., Ballard Food Bank",
            width=280
        )
        
        # Reset button
        self.reset_button = Button(
            label="Reset All Filters",
            button_type="warning",
            width=280
        )
        
        # Results counter
        self.results_div = Div(
            text="<p style='font-size:14px;'>Loading...</p>",
            width=280
        )
    
    def update_eligibility_options(self, unique_groups):
        """
        Populate eligibility options from data.
        
        Parameters:
        -----------
        unique_groups : list
            Unique values from 'who_they_serve' column
        """
        # Clean and sort options
        options = [(g, g) for g in sorted(unique_groups) if g and str(g).strip()]
        self.eligibility_select.options = options
    
    def update_results_display(self, filtered_count, total_count):
        """
        Update results counter.
        
        Parameters:
        -----------
        filtered_count : int
            Number of filtered results
        total_count : int
            Total number of locations
        """
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0
        
        self.results_div.text = f"""
        <div style='
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            color: white;
            text-align: center;
        '>
            <div style='font-size: 32px; font-weight: bold; margin-bottom: 5px;'>
                {filtered_count}
            </div>
            <div style='font-size: 14px; opacity: 0.9;'>
                of {total_count} locations
            </div>
            <div style='font-size: 12px; opacity: 0.8; margin-top: 5px;'>
                ({percentage:.0f}%)
            </div>
        </div>
        """
    
    def create_layout(self):
        """Create complete filter panel layout."""
        
        # Header
        header = Div(
            text="""
            <div style='margin-bottom: 20px;'>
                <h2 style='margin: 0; color: #2c5282;'>🔍 Filter Food Banks</h2>
                <p style='margin: 5px 0 0 0; color: #718096; font-size: 13px;'>
                    Find the right food assistance for your needs
                </p>
            </div>
            """,
            width=280
        )
        
        # Build layout sections
        layout = column(
            header,
            
            # Search
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>🔎 Search</h3>"),
            self.search_input,
            
            # Distance
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>📍 Distance</h3>"),
            self.distance_slider,
            
            # Status
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>✅ Status</h3>"),
            self.open_only_toggle,
            
            # Type
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>🏪 Type</h3>"),
            Div(text="<p style='font-size: 12px; color: #718096; margin: 0 0 8px 0;'>Hold Ctrl/Cmd to select multiple</p>"),
            self.type_select,
            
            # Eligibility
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>👥 Who They Serve</h3>"),
            Div(text="<p style='font-size: 12px; color: #718096; margin: 0 0 8px 0;'>Hold Ctrl/Cmd to select multiple</p>"),
            self.eligibility_select,
            
            # Days
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>📅 Days Open</h3>"),
            Div(text="<p style='font-size: 12px; color: #718096; margin: 0 0 8px 0;'>Select days you need service</p>"),
            self.day_checkboxes,
            
            # Results and actions
            Div(text="<h3 style='margin: 20px 0 8px 0; color: #2d3748;'>📊 Results</h3>"),
            self.results_div,
            self.reset_button,
            
            width=320,
            sizing_mode='fixed'
        )
        
        return layout
    
    def get_all_widgets(self):
        """Return dictionary of all widgets for callback attachment."""
        return {
            'distance_slider': self.distance_slider,
            'type_select': self.type_select,
            'eligibility_select': self.eligibility_select,
            'day_checkboxes': self.day_checkboxes,
            'open_only_toggle': self.open_only_toggle,
            'search_input': self.search_input,
            'reset_button': self.reset_button,
            'results_div': self.results_div
        }
