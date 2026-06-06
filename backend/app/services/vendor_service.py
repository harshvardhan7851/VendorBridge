"""
services/vendor_service.py
==========================
Business logic for Vendor Category and Vendor management.

Enforces:
  - Unique category names.
  - Unique GST / PAN numbers across vendors.
  - Status-based workflow instead of hard deletes.
  - Pagination + search + filter + sort on vendor lists.
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vendor import Vendor, VendorCategory, VendorStatus
from app.schemas.vendor import (
    VendorCategoryCreate,
    VendorCategoryUpdate,
    VendorCreate,
    VendorFilterParams,
    VendorStatusUpdate,
    VendorUpdate,
)


# ===========================================================================
# VendorCategoryService
# ===========================================================================

class VendorCategoryService:
    """CRUD for vendor categories with soft deletes."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_categories(
        self, include_inactive: bool = False
    ) -> list[VendorCategory]:
        query = select(VendorCategory)
        if not include_inactive:
            query = query.where(VendorCategory.is_active == True)  # noqa: E712
        result = await self.db.execute(query.order_by(VendorCategory.name))
        return list(result.scalars().all())

    async def get_category(self, category_id: uuid.UUID) -> VendorCategory:
        result = await self.db.execute(
            select(VendorCategory).where(VendorCategory.id == category_id)
        )
        cat = result.scalar_one_or_none()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor category '{category_id}' not found.",
            )
        return cat

    async def create_category(
        self,
        payload: VendorCategoryCreate,
        created_by_id: uuid.UUID,
    ) -> VendorCategory:
        existing = await self.db.execute(
            select(VendorCategory).where(
                func.lower(VendorCategory.name) == payload.name.lower()
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{payload.name}' already exists.",
            )

        cat = VendorCategory(
            name=payload.name,
            description=payload.description,
            is_active=True,
            updated_by=created_by_id,
        )
        self.db.add(cat)
        await self.db.commit()
        await self.db.refresh(cat)
        return cat

    async def update_category(
        self,
        category_id: uuid.UUID,
        payload: VendorCategoryUpdate,
        updated_by_id: uuid.UUID,
    ) -> VendorCategory:
        cat = await self.get_category(category_id)

        update_data = payload.model_dump(exclude_unset=True)

        # Check name uniqueness if name is being changed
        if "name" in update_data and update_data["name"].lower() != cat.name.lower():
            dup = await self.db.execute(
                select(VendorCategory).where(
                    func.lower(VendorCategory.name) == update_data["name"].lower(),
                    VendorCategory.id != category_id,
                )
            )
            if dup.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category name '{update_data['name']}' already in use.",
                )

        for field, value in update_data.items():
            setattr(cat, field, value)

        cat.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(cat)
        return cat

    async def delete_category(
        self, category_id: uuid.UUID, updated_by_id: uuid.UUID
    ) -> VendorCategory:
        """Soft delete: set is_active = False."""
        cat = await self.get_category(category_id)
        cat.is_active = False
        cat.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(cat)
        return cat


# ===========================================================================
# VendorService
# ===========================================================================

class VendorService:
    """
    Full vendor lifecycle: create, read, update, status changes, and list.
    No hard deletes — status moves to BLACKLISTED or SUSPENDED instead.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # _check_unique_fields
    # ------------------------------------------------------------------

    async def _check_unique_fields(
        self,
        gst_number: str | None,
        pan_number: str | None,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        """Raise 409 if GST or PAN is already registered by another vendor."""
        if gst_number:
            q = select(Vendor).where(Vendor.gst_number == gst_number)
            if exclude_id:
                q = q.where(Vendor.id != exclude_id)
            if (await self.db.execute(q)).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"GST number '{gst_number}' is already registered.",
                )

        if pan_number:
            q = select(Vendor).where(Vendor.pan_number == pan_number)
            if exclude_id:
                q = q.where(Vendor.id != exclude_id)
            if (await self.db.execute(q)).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"PAN number '{pan_number}' is already registered.",
                )

    # ------------------------------------------------------------------
    # get_vendor
    # ------------------------------------------------------------------

    async def get_vendor(self, vendor_id: uuid.UUID) -> Vendor:
        """Fetch vendor with category eagerly loaded. Raises 404 if not found."""
        result = await self.db.execute(
            select(Vendor)
            .options(selectinload(Vendor.category))
            .where(Vendor.id == vendor_id)
        )
        vendor = result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor '{vendor_id}' not found.",
            )
        return vendor

    # ------------------------------------------------------------------
    # list_vendors
    # ------------------------------------------------------------------

    async def list_vendors(
        self,
        filters: VendorFilterParams,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Vendor], int]:
        """
        Paginated vendor list with:
          - full-text search on company_name
          - filter by status and category_id
          - sort by company_name or created_at (asc/desc)
        Returns (items, total_count).
        """
        query = select(Vendor).options(selectinload(Vendor.category))

        # Search
        if filters.search:
            term = f"%{filters.search.lower()}%"
            query = query.where(func.lower(Vendor.company_name).like(term))

        # Filters
        if filters.status:
            query = query.where(Vendor.status == filters.status)

        if filters.category_id:
            query = query.where(Vendor.category_id == filters.category_id)

        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Sort
        sort_col = (
            Vendor.company_name if filters.sort_by == "company_name" else Vendor.created_at
        )
        sort_fn = asc if filters.sort_dir == "asc" else desc
        query = query.order_by(sort_fn(sort_col))

        # Paginate
        offset = (page - 1) * size
        result = await self.db.execute(query.offset(offset).limit(size))
        vendors = list(result.scalars().all())

        return vendors, total

    # ------------------------------------------------------------------
    # create_vendor
    # ------------------------------------------------------------------

    async def create_vendor(
        self,
        payload: VendorCreate,
        created_by_id: uuid.UUID,
    ) -> Vendor:
        await self._check_unique_fields(payload.gst_number, payload.pan_number)

        vendor = Vendor(
            **payload.model_dump(exclude_unset=True),
            status=VendorStatus.PENDING,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        return await self.get_vendor(vendor.id)   # reload with category

    # ------------------------------------------------------------------
    # update_vendor
    # ------------------------------------------------------------------

    async def update_vendor(
        self,
        vendor_id: uuid.UUID,
        payload: VendorUpdate,
        updated_by_id: uuid.UUID,
    ) -> Vendor:
        vendor = await self.get_vendor(vendor_id)

        update_data = payload.model_dump(exclude_unset=True)
        await self._check_unique_fields(
            update_data.get("gst_number"),
            update_data.get("pan_number"),
            exclude_id=vendor_id,
        )

        for field, value in update_data.items():
            setattr(vendor, field, value)

        vendor.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(vendor)
        return await self.get_vendor(vendor_id)

    # ------------------------------------------------------------------
    # update_vendor_status
    # ------------------------------------------------------------------

    async def update_vendor_status(
        self,
        vendor_id: uuid.UUID,
        payload: VendorStatusUpdate,
        updated_by_id: uuid.UUID,
    ) -> Vendor:
        """
        Enforce valid status transitions.
        A blacklisted vendor cannot be activated directly — must go through admin review.
        """
        vendor = await self.get_vendor(vendor_id)

        # Business rule: cannot re-activate a blacklisted vendor directly
        if (
            vendor.status == VendorStatus.BLACKLISTED
            and payload.status == VendorStatus.ACTIVE
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Blacklisted vendors cannot be directly re-activated. "
                    "Move to SUSPENDED first."
                ),
            )

        vendor.status = payload.status
        if payload.remarks is not None:
            vendor.remarks = payload.remarks
        vendor.updated_by = updated_by_id

        await self.db.commit()
        await self.db.refresh(vendor)
        return await self.get_vendor(vendor_id)

    # ------------------------------------------------------------------
    # delete_vendor (not hard delete — sets status BLACKLISTED)
    # ------------------------------------------------------------------

    async def delete_vendor(
        self, vendor_id: uuid.UUID, updated_by_id: uuid.UUID
    ) -> Vendor:
        """
        'Deleting' a vendor means BLACKLISTING it to preserve the audit trail.
        No rows are ever removed from the DB.
        """
        vendor = await self.get_vendor(vendor_id)
        vendor.status = VendorStatus.BLACKLISTED
        vendor.updated_by = updated_by_id
        await self.db.commit()
        await self.db.refresh(vendor)
        return await self.get_vendor(vendor_id)
