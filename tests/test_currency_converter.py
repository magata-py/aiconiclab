import pytest
import requests

from fastapi import HTTPException
from utils.currency_converter import fetch_exchange_rate, round_currency_amount


# Test fetch_exchange_rate

def test_fetch_exchange_rate_success(mocker):
    """Test successful fetch of exchange rate from the API."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"rates": [{"mid": 4.5}]}
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("utils.currency_converter.requests.get", return_value=mock_response)

    rate = fetch_exchange_rate("USD")
    assert rate == 4.5


def test_fetch_exchange_rate_request_exception(mocker):
    """Test fetch_exchange_rate when requests raises a RequestException."""
    mocker.patch("utils.currency_converter.requests.get", side_effect=requests.exceptions.RequestException("Network error"))

    with pytest.raises(HTTPException) as exc_info:
        fetch_exchange_rate("USD")
    assert exc_info.value.status_code == 503
    assert "Currency service unavailable" in exc_info.value.detail


def test_fetch_exchange_rate_key_error(mocker):
    """Test fetch_exchange_rate when API response has missing data (KeyError)."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"rates": []}  # Invalid structure
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("utils.currency_converter.requests.get", return_value=mock_response)

    with pytest.raises(HTTPException) as exc_info:
        fetch_exchange_rate("USD")
    assert exc_info.value.status_code == 400
    assert "Invalid response structure" in exc_info.value.detail


# Test round_currency_amount

@pytest.mark.parametrize("amount, currency, expected", [
    (123.456, "PLN", 123.46),
    (123.456, "USD", 123.46),
    (123.456, "EUR", 123.46),
    (123.456, "GBP", 123.46),
    (123.456, "JPY", 123),  # No decimal places for Yen
    (123.456, "UNKNOWN", 123.46),  # Default precision
])
def test_round_currency_amount(amount, currency, expected):
    """Test rounding of currency amount based on currency precision."""
    result = round_currency_amount(amount, currency)
    assert result == expected
