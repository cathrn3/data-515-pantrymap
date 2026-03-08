import unittest
from pantry_map.utilities.utility import validate_address, geocode_address

class TestAddressValidation(unittest.TestCase):
    """Unit tests for the validate_address function."""

    def test_valid_address(self):
        """Test that a non-empty address is considered valid."""
        valid, msg = validate_address("123 Main St")
        self.assertTrue(valid)
        self.assertEqual(msg, "")

    def test_empty_address(self):
        """Test that an empty string is considered invalid."""
        valid, msg = validate_address("")
        self.assertFalse(valid)
        self.assertEqual(msg, "Address cannot be empty.")

    def test_whitespace_address(self):
        """Test that an address with only spaces is considered invalid."""
        valid, msg = validate_address("   ")
        self.assertFalse(valid)

class TestGeocode(unittest.TestCase):
    """Unit tests for the geocode_address function."""

    def test_known_location(self):
        """Test that a known location returns valid latitude and longitude."""
        coords = geocode_address("Seattle WA")
        self.assertIsNotNone(coords)
        lat, lon = coords
        self.assertTrue(-180 <= lon <= 180)
        self.assertTrue(-90 <= lat <= 90)

    def test_invalid_location(self):
        """Test that an invalid address returns None."""
        coords = geocode_address("ThisAddressDoesNotExistXYZ")
        self.assertIsNone(coords)

if __name__ == "__main__":
    unittest.main()