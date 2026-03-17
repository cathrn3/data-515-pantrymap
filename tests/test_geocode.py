import unittest
from unittest.mock import patch
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from pantry_map.utilities.utility import validate_address, geocode_address
from unittest.mock import patch, MagicMock

# Mocked location object
def mock_location(lat, lon):
    m = MagicMock()
    m.latitude = lat
    m.longitude = lon
    return m

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

    @patch("pantry_map.utilities.utility.Nominatim.geocode")
    def test_known_location(self, mock_geocode):
        """Test that a known location returns valid latitude and longitude."""
        
        mock_geocode.return_value = mock_location(47.6083, -122.3355)

        lat, lon = geocode_address("85 Pike St. Seattle WA")
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lon)
        self.assertTrue(47.0 <= lat <= 48.0)
        self.assertTrue(-123.0 <= lon <= -121.5)
        print(lat, lon)

    @patch("pantry_map.utilities.utility.Nominatim.geocode")
    def test_invalid_location(self, mock_geocode):
        """Test that an invalid address returns None."""
        
        mock_geocode.return_value = None
        
        lat, lon = geocode_address("ThisAddressDoesNotExistXYZ")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    @patch("pantry_map.utilities.utility.Nominatim.geocode")
    def test_geocoder_timeout(self, mock_geocode):
        """Test that GeocoderTimedOut is handled and returns None after retries."""
        mock_geocode.side_effect = GeocoderTimedOut("Service timed out")
        lat, lon = geocode_address("Some Address")
        self.assertIsNone(lat)
        self.assertIsNone(lon)
        self.assertEqual(mock_geocode.call_count, 2)

    @patch("pantry_map.utilities.utility.Nominatim.geocode")
    def test_geocoder_service_error(self, mock_geocode):
        """Test that GeocoderServiceError is handled and returns None."""
        mock_geocode.side_effect = GeocoderServiceError("Service unavailable")
        lat, lon = geocode_address("Some Address")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

if __name__ == "__main__":
    unittest.main()