
import requests
from fastapi import HTTPException


def fetch_exchange_rate(target_currency: str) -> float:
    """Fetches the exchange rate for a given currency, using cache if available."""

    # Fetch rate from NBP API
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{target_currency}/?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if rates list is not empty
        if not data.get("rates") or not isinstance(data["rates"], list):
            raise HTTPException(status_code=400, detail="Invalid response structure from currency API")

        rate = data["rates"][0]["mid"]
        return rate
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Currency service unavailable: {e}")
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid response structure from currency API")


def round_currency_amount(amount: float, currency: str) -> float:
    """Round the converted amount based on the currency's standard precision."""
    currency_precision = {
        "PLN": 2,
        "USD": 2,
        "EUR": 2,
        "GBP": 2,
        "JPY": 0,  # Yen - no decimal places
    }

    precision = currency_precision.get(currency, 2)
    return round(amount, precision)