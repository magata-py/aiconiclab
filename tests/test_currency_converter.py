import pytest
import os
import json
import time
from unittest.mock import patch

from utils import currency_converter
from utils.currency_converter import CACHE_FILE, update_cache, fetch_exchange_rate, CACHE_EXPIRATION_SECONDS, \
    clean_cache


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """Fixture to set up and tear down the cache file for tests."""
    # Ensure cache file is cleaned up before and after each test
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    yield
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)


def test_fetch_exchange_rate_with_cache(mocker):
    """Test that fetch_exchange_rate uses the cache if available."""
    # Add a cached rate
    update_cache("USD", 4.5)
    # Mock the API call to prevent real HTTP requests
    mocker.patch("currency_converter.requests.get")

    # Fetch rate for USD - should use cache, not API
    rate = fetch_exchange_rate("USD")
    assert rate == 4.5
    currency_converter.requests.get.assert_not_called()


def test_fetch_exchange_rate_without_cache(mocker):
    """Test that fetch_exchange_rate calls API if cache is not available."""
    # Mock the API response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"rates": [{"mid": 4.0}]}
    mocker.patch("currency_converter.requests.get", return_value=mock_response)

    # Fetch rate for USD - should call API
    rate = fetch_exchange_rate("USD")
    assert rate == 4.0
    currency_converter.requests.get.assert_called_once()


def test_clean_cache(cache):
    """Test that clean_cache removes expired entries from the cache."""
    # Add an expired and a valid cache entry
    update_cache("USD", 4.5)
    time.sleep(1)  # Ensure there's a time difference
    expired_timestamp = time.time() - CACHE_EXPIRATION_SECONDS - 1
    with open(CACHE_FILE, "r+") as file:
        cache = json.load(file)
        cache["EXPIRED"] = (expired_timestamp, 3.5)
        file.seek(0)
        json.dump(cache, file)
        file.truncate()

    # Run clean_cache and check that expired entry is removed
    clean_cache()
    with open(CACHE_FILE, "r") as file:
        cache = json.load(file)

    assert "EXPIRED" not in cache
    assert "USD" in cache  # USD entry should still be present


def test_fetch_exchange_rate_with_expired_cache(mocker):
    """Test that fetch_exchange_rate calls API if cache entry is expired."""
    # Set up expired cache entry
    expired_timestamp = time.time() - CACHE_EXPIRATION_SECONDS - 1
    with open(CACHE_FILE, "w") as file:
        json.dump({"USD": (expired_timestamp, 4.5)}, file)

    # Mock the API response
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"rates": [{"mid": 4.0}]}
    mocker.patch("currency_converter.requests.get", return_value=mock_response)

    # Fetch rate for USD - should ignore expired cache and call API
    rate = fetch_exchange_rate("USD")
    assert rate == 4.0
    currency_converter.requests.get.assert_called_once()
