"""
Quotations Router — Placeholder endpoints.
"""
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List Quotations")
async def list_quotations():
    # TODO: Filter by rfq_id, vendor_id, status
    return NOT_IMPLEMENTED


@router.post("/", summary="Submit Quotation", status_code=201)
async def create_quotation():
    # TODO: Validate QuotationCreate, link to RFQ and Vendor
    return NOT_IMPLEMENTED


@router.get("/{quotation_id}", summary="Get Quotation")
async def get_quotation(quotation_id: UUID):
    # TODO: Return quotation with line items
    return NOT_IMPLEMENTED


@router.put("/{quotation_id}", summary="Update Quotation")
async def update_quotation(quotation_id: UUID):
    # TODO: Only allow updates when status is "draft"
    return NOT_IMPLEMENTED


@router.post("/{quotation_id}/award", summary="Award Quotation")
async def award_quotation(quotation_id: UUID):
    # TODO: Mark quotation as "awarded", generate Purchase Order
    return NOT_IMPLEMENTED
