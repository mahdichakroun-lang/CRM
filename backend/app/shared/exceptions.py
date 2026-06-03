"""
Shared exception classes used across all domains.
"""
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id {entity_id} not found",
        )


class AlreadyExistsException(HTTPException):
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity} with {field} '{value}' already exists",
        )


class ForbiddenException(HTTPException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Invalid or expired credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequestException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
