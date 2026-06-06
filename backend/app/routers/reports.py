"""
Reports Router — Placeholder endpoints.
"""
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/spend-by-vendor", summary="Spend Analysis by Vendor")
async def spend_by_vendor():
    # TODO: Aggregate total PO/Invoice amounts grouped by vendor
    return NOT_IMPLEMENTED


@router.get("/rfq-summary", summary="RFQ Summary Report")
async def rfq_summary():
    # TODO: RFQ counts grouped by status, category, time period
    return NOT_IMPLEMENTED


@router.get("/approval-cycle-time", summary="Approval Cycle Time")
async def approval_cycle_time():
    # TODO: Average time from request to approval, by type
    return NOT_IMPLEMENTED


@router.get("/vendor-performance", summary="Vendor Performance Metrics")
async def vendor_performance():
    # TODO: On-time delivery rate, invoice accuracy, quotation win rate
    return NOT_IMPLEMENTED


@router.get("/export/pdf", summary="Export Report as PDF")
async def export_pdf():
    # TODO: Generate PDF report using pdf_service, stream as response
    return NOT_IMPLEMENTED
