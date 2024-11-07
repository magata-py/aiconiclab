from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError
import logging

# Initialize logger for error tracking
logger = logging.getLogger(__name__)


class CustomExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Middleware to handle exceptions and return uniform error responses.
        This middleware catches specific errors (e.g., database integrity errors)
        and any unexpected exceptions, providing standardized JSON responses.
        """
        try:
            # Attempt to process the request
            response = await call_next(request)
            return response
        except IntegrityError as e:
            # Handle database integrity errors (e.g., unique constraint violations)
            logger.error(f"Database integrity error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={"detail": "Database integrity error. Please check your data for duplicates or constraints."}
            )
        except HTTPException as e:
            # Catch HTTPException and log the details
            logger.warning(f"HTTP error: {str(e.detail)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Handle any unexpected errors
            logger.error(f"Unexpected error on {request.method} {request.url.path}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred. Please try again later or contact support."}
            )


def init_error_handler(app: FastAPI):
    """
    Function to initialize the custom exception middleware for the FastAPI app.
    This centralizes error handling and ensures consistent error responses.
    """
    app.add_middleware(CustomExceptionMiddleware)  # type: ignore
