import pytest
from unittest.mock import patch, MagicMock
from api import fetch_rates, API_URL
import requests


class TestFetchRates:
    def test_fetch_rates_success(self):
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
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_rates()

            mock_get.assert_called_once_with(API_URL)
            mock_response.raise_for_status.assert_called_once()
            mock_response.json.assert_called_once()

            assert result == mock_response_data['Valute']
            assert 'USD' in result
            assert 'EUR' in result
            assert result['USD']['Value'] == 75.5
            assert result['EUR']['Value'] == 82.3

    def test_fetch_rates_http_error(self):
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
            mock_get.return_value = mock_response

            with pytest.raises(RuntimeError, match='Failed to fetch rates: 404 Not Found'):
                fetch_rates()

    def test_fetch_rates_connection_error(self):
        with patch('api.requests.get') as mock_get:
            mock_get.return_value = requests.ConnectionError('Connection failed')

            with pytest.raises(RuntimeError, match='Failed to fetch rates: Connection failed'):
                fetch_rates()

    def test_fetch_rates_connection_error(self):
        with patch('api.requests.get') as mock_get:
            mock_get.return_value = requests.Timeout('Request timed out')

            with pytest.raises(RuntimeError, match='Failed to fetch rates: Request timed out'):
                fetch_rates()

    def test_fetch_rates_data_structure(self):
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
            }
        }
        with patch('api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_rates()

            assert 'USD' in result
            usd_data = result['USD']
            assert 'ID' in usd_data
            assert 'CharCode' in usd_data
            assert 'Value' in usd_data
            assert 'Name' in usd_data
            assert 'NumCode' in usd_data
            assert 'Nominal' in usd_data
            assert 'Previous' in usd_data
            assert usd_data['CharCode'] == 'USD'
            assert isinstance(usd_data['Value'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__])
