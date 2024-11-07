from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.order import Order
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, VALID_STATUSES
from utils.currency_converter import fetch_exchange_rate
from utils.database import get_db

router = APIRouter()


def calculate_converted_amount(total_amount: float, target_currency: str) -> float:
    """Helper function to fetch exchange rate and calculate the converted amount."""
    if target_currency == "PLN":
        return total_amount
    exchange_rate = fetch_exchange_rate(target_currency)
    return round(total_amount / exchange_rate, 2)


@router.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Create a new order record in the database
    db_order = Order(
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        currency=order.currency
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/orders/{order_id}/", response_model=OrderResponse)
def update_order_status(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    # Fetch the order by ID
    db_order = db.query(Order).filter(Order.id == order_id).first()  # type: ignore
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update the status of the order
    db_order.status = order.status
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders/{order_id}/", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    # Retrieve the order by ID
    db_order = db.query(Order).filter(Order.id == order_id).first()  # type: ignore
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Calculate the converted amount using a helper function
    converted_amount = calculate_converted_amount(db_order.total_amount, db_order.currency)

    # Prepare the response
    response = OrderResponse(
        id=db_order.id,
        customer_name=db_order.customer_name,
        total_amount=db_order.total_amount,
        currency=db_order.currency,
        status=db_order.status,
        converted_amount=converted_amount
    )
    return response


@router.get("/orders/", response_model=list[OrderResponse])
def list_orders(
        status: str = None,
        db: Session = Depends(get_db)
):
    """
    Retrieve a list of orders with optional filtering by status and pagination.
    - status: Filter orders by status (optional)
    - limit: Limit the number of results (default: 10, max: 100)
    - offset: Number of records to skip before starting to return results (default: 0)
    """
    query = db.query(Order)

    # Validate and apply status filter if provided
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid status provided")
        query = query.filter(Order.status == status)  # type: ignore

    orders = query.all()
    return orders