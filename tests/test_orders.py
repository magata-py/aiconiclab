# tests/test_orders.py
import pytest
from fastapi.testclient import TestClient
from main import app
from utils.currency_converter import round_currency_amount
from utils.database import SessionLocal, Base, engine  # Import from utils.database
from models.order import Order


# Create a test client
client = TestClient(app)


# Fixture to set up a test database (SQLite in-memory)
@pytest.fixture(scope="module")
def test_db():
    # Create tables for testing
    Base.metadata.create_all(bind=engine)
    yield SessionLocal()  # Yield the test session
    # Drop tables after tests complete
    Base.metadata.drop_all(bind=engine)


def test_create_order(test_db):
    """Test creating a new order."""
    response = client.post(
        "/orders/",
        json={
            "customer_name": "Test Customer",
            "total_amount": 100.0,
            "currency": "USD"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert data["total_amount"] == 100.0
    assert data["currency"] == "USD"
    assert data["status"] == "pending"


def test_update_order_status(test_db):
    """Test updating the status of an order."""
    # First, create an order
    response = client.post(
        "/orders/",
        json={
            "customer_name": "Another Customer",
            "total_amount": 50.0,
            "currency": "EUR"
        }
    )
    order_id = response.json()["id"]

    # Update the status
    response = client.put(f"/orders/{order_id}/", json={"status": "shipped"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "shipped"


def test_get_order_with_conversion(test_db, mocker):
    """Test retrieving an order with currency conversion."""
    # Use mocking to simulate a response from the NBP currency API
    mocker.patch("utils.currency_converter.fetch_exchange_rate", return_value=3.9869)

    # Create an order
    response = client.post(
        "/orders/",
        json={
            "customer_name": "Currency Customer",
            "total_amount": 100.0,
            "currency": "USD"
        }
    )
    order_id = response.json()["id"]

    # Retrieve the order with conversion
    response = client.get(f"/orders/{order_id}/")
    assert response.status_code == 200
    data = response.json()

    # Apply the same rounding logic as in the production code
    expected_converted_amount = round_currency_amount(100.0 * 3.9869)
    assert data["converted_amount"] == expected_converted_amount
