"""
schemas/report.py
"""
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
import uuid

class ProcurementSummaryResponse(BaseModel):
    total_rfqs: int
    total_purchase_orders: int
    total_invoices: int
    total_spend: Decimal
    pending_approvals: int

class VendorPerformanceResponse(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str
    approved_orders: int
    total_spend: Decimal
    average_order_value: Decimal

class MonthlySpendResponse(BaseModel):
    month: str
    amount: Decimal
