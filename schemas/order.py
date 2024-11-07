from pydantic import BaseModel, Field, constr, condecimal, ConfigDict
from typing import Optional, Literal, List

VALID_STATUSES = {"pending", "shipped", "delivered", "in-progress"}


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100, description="Full name of the customer")
    total_amount: condecimal(gt=0, decimal_places=2) = Field(..., description="Total amount of the order in PLN")
    currency: Literal["PLN", "USD", "EUR", "GBP"] = Field(..., description="Currency for the order (PLN, USD,  EUR, "
                                                                           "GBP)")


class OrderUpdate(BaseModel):
    status: Literal["pending", "in-progress", "shipped", "delivered"] = Field(..., description="Status of the order")


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: float
    currency: str
    status: str
    converted_amount: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


