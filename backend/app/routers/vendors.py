"""
Vendors Router
==============
Endpoints:
  GET    /api/v1/vendors          - List all vendors
  POST   /api/v1/vendors          - Register a new vendor
  GET    /api/v1/vendors/{id}     - Get vendor details
  PUT    /api/v1/vendors/{id}     - Update vendor details
  DELETE /api/v1/vendors/{id}     - Deactivate a vendor
  POST   /api/v1/vendors/{id}/approve - Approve a vendor
  POST   /api/v1/vendors/{id}/reject  - Reject a vendor
"""

from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List Vendors")
async def list_vendors():
    # TODO: Fetch paginated vendors from DB, apply filters (status, category)
    return NOT_IMPLEMENTED


@router.post("/", summary="Register Vendor", status_code=201)
async def create_vendor():
    # TODO: Validate VendorCreate, check duplicate, insert to DB, notify admin
    return NOT_IMPLEMENTED


@router.get("/{vendor_id}", summary="Get Vendor")
async def get_vendor(vendor_id: UUID):
    # TODO: Fetch vendor by ID, raise 404 if not found
    return NOT_IMPLEMENTED


@router.put("/{vendor_id}", summary="Update Vendor")
async def update_vendor(vendor_id: UUID):
    # TODO: Validate VendorUpdate, apply changes, return updated VendorResponse
    return NOT_IMPLEMENTED


@router.delete("/{vendor_id}", summary="Deactivate Vendor", status_code=204)
async def delete_vendor(vendor_id: UUID):
    # TODO: Soft-delete (set is_active=False), restricted to admin role
    return NOT_IMPLEMENTED


@router.post("/{vendor_id}/approve", summary="Approve Vendor")
async def approve_vendor(vendor_id: UUID):
    # TODO: Set vendor status to "approved", send notification email to vendor
    return NOT_IMPLEMENTED


@router.post("/{vendor_id}/reject", summary="Reject Vendor")
async def reject_vendor(vendor_id: UUID):
    # TODO: Set vendor status to "rejected", send rejection email with reason
    return NOT_IMPLEMENTED
