from fastapi import FastAPI

from middleware.error_handler import init_error_handler
from routes.order_routes import router as order_router
from utils.database import Base, engine

# Generate tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Management API",
    description="API for managing orders and currency conversions.",
    version="1.0.0"
)
# Initialize custom error handler middleware
init_error_handler(app)

# Register the order routes with the main app
app.include_router(order_router)
