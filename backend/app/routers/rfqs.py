"""
RFQs Router
===========
Endpoints:
  GET    /api/v1/rfqs              - List all RFQs
  POST   /api/v1/rfqs              - Create a new RFQ
  GET    /api/v1/rfqs/{id}         - Get RFQ details
  PUT    /api/v1/rfqs/{id}         - Update an RFQ
  DELETE /api/v1/rfqs/{id}         - Cancel an RFQ
  POST   /api/v1/rfqs/{id}/publish - Publish RFQ to vendors
"""

from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List RFQs")
async def list_rfqs():
    # TODO: Paginated list with filters (status, category, date range)
    return NOT_IMPLEMENTED


@router.post("/", summary="Create RFQ", status_code=201)
async def create_rfq():
    # TODO: Validate RFQCreate, auto-generate rfq_number, insert to DB
    return NOT_IMPLEMENTED


@router.get("/{rfq_id}", summary="Get RFQ")
async def get_rfq(rfq_id: UUID):
    # TODO: Fetch RFQ with line_items eagerly loaded
    return NOT_IMPLEMENTED


@router.put("/{rfq_id}", summary="Update RFQ")
async def update_rfq(rfq_id: UUID):
    # TODO: Only allow updates when status is "draft"
    return NOT_IMPLEMENTED


@router.delete("/{rfq_id}", summary="Cancel RFQ", status_code=204)
async def cancel_rfq(rfq_id: UUID):
    # TODO: Soft-cancel (status = "cancelled"), notify assigned vendors
    return NOT_IMPLEMENTED


@router.post("/{rfq_id}/publish", summary="Publish RFQ to Vendors")
async def publish_rfq(rfq_id: UUID):
    # TODO: Set status="published", send invitation emails to selected vendors
    return NOT_IMPLEMENTED
