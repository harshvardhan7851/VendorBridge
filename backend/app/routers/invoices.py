"""
Invoices Router — Placeholder endpoints.
"""
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List Invoices")
async def list_invoices():
    # TODO: Filter by status, vendor, PO, date range
    return NOT_IMPLEMENTED


@router.post("/", summary="Submit Invoice", status_code=201)
async def create_invoice():
    # TODO: Validate InvoiceCreate, link to PurchaseOrder
    return NOT_IMPLEMENTED


@router.get("/{invoice_id}", summary="Get Invoice")
async def get_invoice(invoice_id: UUID):
    return NOT_IMPLEMENTED


@router.post("/{invoice_id}/approve", summary="Approve Invoice")
async def approve_invoice(invoice_id: UUID):
    # TODO: Set status="approved", initiate payment workflow
    return NOT_IMPLEMENTED


@router.post("/{invoice_id}/reject", summary="Reject Invoice")
async def reject_invoice(invoice_id: UUID):
    # TODO: Set status="rejected", notify vendor with reason
    return NOT_IMPLEMENTED
