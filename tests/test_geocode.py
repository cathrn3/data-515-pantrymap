import unittest
from pantry_map.utilities.utility import validate_address, geocode_address

class TestAddressValidation(unittest.TestCase):
    """Unit tests for the validate_address function."""

    def test_valid_address(self):
        """Test that a non-empty address is considered valid."""
        valid, msg, address = validate_address("123 Main St")
        self.assertTrue(valid)
        self.assertEqual(msg, "")

    def test_empty_address(self):
        """Test that an empty string is considered invalid."""
        valid, msg, address = validate_address("")
        self.assertFalse(valid)
        self.assertEqual(msg, "Address cannot be empty.")

    def test_whitespace_address(self):
        """Test that an address with only spaces is considered invalid."""
        valid, msg, address = validate_address("   ")
        self.assertFalse(valid)

class TestGeocode(unittest.TestCase):
    """Unit tests for the geocode_address function."""

    def test_known_location(self):
        """Test that a known location returns valid latitude and longitude."""
        
        lat, lon = geocode_address("85 Pike St. Seattle WA")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lon)
        self.assertTrue(47.0 <= lat <= 48.0)
        self.assertTrue(-123.0 <= lon <= -121.5)
        print(lat, lon)

    def test_invalid_location(self):
        """Test that an invalid address returns None."""
        lat, lon = geocode_address("ThisAddressDoesNotExistXYZ")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

if __name__ == "__main__":
    unittest.main()