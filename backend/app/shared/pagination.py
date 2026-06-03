"""
Pagination utilities for API responses.
"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
import math

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Input pagination parameters."""
    page: int = 1
    size: int = 20
    search: Optional[str] = None

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size > 0 else 0,
        )
