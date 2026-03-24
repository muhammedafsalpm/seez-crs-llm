from fastapi import HTTPException, status


class CRSException(HTTPException):
    """Base exception for CRS"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class RateLimitException(CRSException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class ModelNotLoadedException(CRSException):
    """Model not loaded"""
    def __init__(self, detail: str = "Model not loaded"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="MODEL_NOT_LOADED"
        )


class InvalidUserException(CRSException):
    """Invalid user ID"""
    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
            error_code="INVALID_USER"
        )
