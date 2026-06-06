"""
schemas/pagination.py
======================
Generic pagination wrappers used across all list endpoints.
"""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PagedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response envelope.
    Usage:
        return PagedResponse[VendorResponse](
            items=vendors, total=100, page=1, size=20
        )
    """
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int,
    ) -> "PagedResponse[T]":
        import math
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size else 0,
        )
