import pytest
import pandas as pd
from filters.manager import FilterManager

def test_filter_by_distance():
    data = pd.DataFrame({
        'latitude': [47.6062, 47.6640],
        'longitude': [-122.3321, -122.3741],
        'food_resource_type': ['Food Bank', 'Meal']
    })
    
    manager = FilterManager(data)
    manager.set_user_location(47.6062, -122.3321)
    manager.filter_by_distance(5)
    
    assert manager.get_count() == 2  # Both within 5 miles

def test_empty_results():
    data = pd.DataFrame({
        'latitude': [47.6062],
        'longitude': [-122.3321],
        'food_resource_type': ['Food Bank']
    })
    
    manager = FilterManager(data)
    manager.filter_by_type(['Meal'])  # No meals
    
    assert manager.get_count() == 0

def test_filter_chaining():
    # Test multiple filters applied in sequence
    pass
