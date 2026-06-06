"""
Purchase Orders Router — Placeholder endpoints.
"""
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List Purchase Orders")
async def list_purchase_orders():
    # TODO: Paginated list with filters (status, vendor, date range)
    return NOT_IMPLEMENTED


@router.post("/", summary="Create Purchase Order", status_code=201)
async def create_purchase_order():
    # TODO: Validate PurchaseOrderCreate, auto-generate po_number
    return NOT_IMPLEMENTED


@router.get("/{po_id}", summary="Get Purchase Order")
async def get_purchase_order(po_id: UUID):
    # TODO: Return PO with line items and vendor details
    return NOT_IMPLEMENTED


@router.put("/{po_id}", summary="Update Purchase Order")
async def update_purchase_order(po_id: UUID):
    return NOT_IMPLEMENTED


@router.post("/{po_id}/send", summary="Send PO to Vendor")
async def send_purchase_order(po_id: UUID):
    # TODO: Send PO PDF to vendor via email, set status="sent"
    return NOT_IMPLEMENTED
