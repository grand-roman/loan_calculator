import pytest
import requests
from unittest.mock import patch, MagicMock
from api import fetch_rates, API_URL


class TestFetchRates:
    """Test class for fetch_rates function in api.py"""
    
    def test_fetch_rates_success(self):
        """Test successful API response with valid data"""
        # Mock response data
        mock_response_data = {
            "success": True,
            "Valute": {
                "USD": {
                    "ID": "R01235",
                    "NumCode": "840",
                    "CharCode": "USD",
                    "Nominal": 1,
                    "Name": "Доллар США",
                    "Value": 75.5,
                    "Previous": 75.0
                },
                "EUR": {
                    "ID": "R01239",
                    "NumCode": "978",
                    "CharCode": "EUR",
                    "Nominal": 1,
                    "Name": "Евро",
                    "Value": 82.3,
                    "Previous": 82.0
                }
            }
        }
        
        with patch('api.requests.get') as mock_get:
            # Mock the response object
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_rates()
            
            # Verify the function was called correctly
            mock_get.assert_called_once_with(API_URL)
            mock_response.raise_for_status.assert_called_once()
            mock_response.json.assert_called_once()
            
            # Verify the result
            assert result == mock_response_data['Valute']
            assert 'USD' in result
            assert 'EUR' in result
            assert result['USD']['Value'] == 75.5
            assert result['EUR']['Value'] == 82.3
    
    def test_fetch_rates_success_without_success_field(self):
        """Test successful API response when success field is missing (defaults to True)"""
        mock_response_data = {
            "Valute": {
                "USD": {
                    "ID": "R01235",
                    "CharCode": "USD",
                    "Value": 75.5
                }
            }
        }
        
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_rates()
            
            assert result == mock_response_data['Valute']
            assert 'USD' in result
    
    def test_fetch_rates_http_error(self):
        """Test HTTP error handling (404, 500, etc.)"""
        with patch('api.requests.get') as mock_get:
            # Mock HTTP error
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            with pytest.raises(RuntimeError, match="Failed to fetch rates: 404 Not Found"):
                fetch_rates()
    
    def test_fetch_rates_connection_error(self):
        """Test network connection error"""
        with patch('api.requests.get') as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection failed")
            
            with pytest.raises(RuntimeError, match="Failed to fetch rates: Connection failed"):
                fetch_rates()
    
    def test_fetch_rates_timeout_error(self):
        """Test request timeout error"""
        with patch('api.requests.get') as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")
            
            with pytest.raises(RuntimeError, match="Failed to fetch rates: Request timed out"):
                fetch_rates()
    
    def test_fetch_rates_empty_valute(self):
        """Test API response with empty Valute field"""
        mock_response_data = {
            "success": True,
            "Valute": {}
        }
        
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_rates()
            
            assert result == {}
            assert len(result) == 0
    
    def test_fetch_rates_malformed_json(self):
        """Test response with malformed JSON"""
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)
            mock_get.return_value = mock_response
            
            with pytest.raises(RuntimeError, match="Failed to fetch rates:"):
                fetch_rates()
    
    def test_fetch_rates_ssl_error(self):
        """Test SSL certificate error"""
        with patch('api.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.SSLError("SSL certificate verification failed")
            
            with pytest.raises(RuntimeError, match="Failed to fetch rates: SSL certificate verification failed"):
                fetch_rates()

class TestApiIntegration:
    """Integration tests for API functionality"""
    
    def test_fetch_rates_return_type(self):
        """Test that fetch_rates returns the correct type"""
        mock_response_data = {
            "success": True,
            "Valute": {"USD": {"Value": 75.5}}
        }
        
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_rates()
            
            assert isinstance(result, dict)
            assert isinstance(result, dict)  # Valute should be a dict
    
    def test_fetch_rates_data_structure(self):
        """Test the structure of returned data"""
        mock_response_data = {
            "success": True,
            "Valute": {
                "USD": {
                    "ID": "R01235",
                    "CharCode": "USD",
                    "Value": 75.5,
                    "Name": "Доллар США"
                }
            }
        }
        
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = fetch_rates()
            
            # Test data structure
            assert 'USD' in result
            usd_data = result['USD']
            assert 'ID' in usd_data
            assert 'CharCode' in usd_data
            assert 'Value' in usd_data
            assert 'Name' in usd_data
            assert usd_data['CharCode'] == 'USD'
            assert isinstance(usd_data['Value'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__])
