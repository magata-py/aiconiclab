import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from models.order import Order
from utils.database import get_db

client = TestClient(app)


# Dependency override for testing
@pytest.fixture
def db_session(mocker):
    db = mocker.Mock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()


# Test create_order
def test_create_order(db_session):
    """Test creating a new order."""
    # Mock order returned from the database after creation
    db_order = Order(id=1, customer_name="John Doe", total_amount=100.0, currency="USD", status="pending")
    db_session.add.return_value = None
    db_session.commit.return_value = None
    db_session.refresh.side_effect = lambda x: setattr(x, "id", 1) or setattr(x, "status", "pending") or x
    # Mock the return of the created order from query
    db_session.query.return_value.filter.return_value.first.return_value = db_order

    # Make request to create order
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "total_amount": 100.0,
            "currency": "USD"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["total_amount"] == 100.0
    assert data["currency"] == "USD"
    assert data["status"] == "pending"
    assert data["id"] == 1  # Now we ensure 'id' is set correctly


# Test update_order_status
def test_update_order_status(db_session):
    """Test updating the order status."""
    db_order = Order(id=1, customer_name="John Doe", total_amount=100.0, currency="USD", status="pending")
    db_session.query.return_value.filter.return_value.first.return_value = db_order
    db_session.commit.return_value = None
    db_session.refresh.side_effect = lambda x: x

    response = client.put(
        "/orders/1/",
        json={"status": "shipped"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shipped"


# Test get_order
def test_get_order(db_session, mocker):
    """Test retrieving an order with currency conversion."""
    db_order = Order(id=1, customer_name="John Doe", total_amount=100.0, currency="USD", status="pending")
    db_session.query.return_value.filter.return_value.first.return_value = db_order
    mocker.patch("routes.order_routes.fetch_exchange_rate", return_value=4.5)

    response = client.get("/orders/1/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["customer_name"] == "John Doe"
    assert data["total_amount"] == 100.0
    assert data["currency"] == "USD"
    assert data["converted_amount"] == 22.22  # 100 / mocked rate 4.5


# Test list_orders with pagination and status filter
@pytest.mark.parametrize("status, expected_status", [
    ("pending", "pending"),
    ("shipped", "shipped"),
    (None, None)  # Set expected_status to None if no filter is applied
])
def test_list_orders(db_session, status, expected_status):
    """Test listing orders with optional status filter."""
    # Define the mock orders that should be returned by the query based on the filter
    all_orders = [
        Order(id=1, customer_name="John Doe", total_amount=100.0, currency="USD", status="pending"),
        Order(id=2, customer_name="Jane Doe", total_amount=200.0, currency="EUR", status="shipped")
    ]

    # Configure the mock query based on whether a status filter is applied
    if status:
        filtered_orders = [order for order in all_orders if order.status == status]
        db_session.query.return_value.filter.return_value.all.return_value = filtered_orders
    else:
        db_session.query.return_value.all.return_value = all_orders  # No filtering, return all orders

    # Build the query URL with the status parameter if provided
    url = "/orders/"
    if status:
        url += f"?status={status}"

    # Make the GET request to the orders endpoint
    response = client.get(url)

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # If status filter is applied, check that each order has the expected status
    if status:
        for order in data:
            assert order["status"] == expected_status
