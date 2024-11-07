from typing import Any

import requests
import json
import os
import time
from fastapi import HTTPException


def fetch_exchange_rate(target_currency: str) -> float:
    """Fetches the exchange rate for a given currency, using cache if available."""

    # Fetch rate from NBP API
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{target_currency}/?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        rate = data["rates"][0]["mid"]

        return rate
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Currency service unavailable: {e}")
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid response structure from currency API")
