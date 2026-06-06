"""
Pagination Helper
=================
Reusable pagination utilities for list endpoints.
"""

from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Usage:
        return PaginatedResponse[VendorResponse](
            items=vendors,
            total=total_count,
            page=1,
            size=20,
        )
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int = 0

    def model_post_init(self, __context):
        # TODO: Calculate total pages
        # self.pages = math.ceil(self.total / self.size)
        pass
