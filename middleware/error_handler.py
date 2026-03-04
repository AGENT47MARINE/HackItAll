"""Error handling middleware."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Union

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            errors.append({
                "field": field,
                "message": message,
                "type": error["type"]
            })
        
        logger.warning(f"Validation error on {request.url.path}: {errors}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Invalid input data",
                "details": errors
            }
        )
    
    @staticmethod
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors."""
        logger.error(f"Database error on {request.url.path}: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "message": "An error occurred while processing your request"
            }
        )
    
    @staticmethod
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle generic exceptions."""
        logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )


def setup_error_handlers(app):
    """Setup error handlers for the FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import SQLAlchemyError
    
    app.add_exception_handler(
        RequestValidationError,
        ErrorHandler.validation_exception_handler
    )
    
    app.add_exception_handler(
        SQLAlchemyError,
        ErrorHandler.database_exception_handler
    )
    
    app.add_exception_handler(
        Exception,
        ErrorHandler.generic_exception_handler
    )
