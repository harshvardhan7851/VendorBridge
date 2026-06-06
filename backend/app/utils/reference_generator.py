"""
Reference Number Generator
===========================
Utility for generating sequential reference numbers for
RFQs, Quotations, Purchase Orders, and Invoices.
"""

import uuid
from datetime import datetime, timezone

def _generate_reference(prefix: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{today}-{suffix}"

def generate_rfq_number() -> str:
    return _generate_reference("RFQ")

def generate_quotation_number() -> str:
    return _generate_reference("QT")

def generate_po_number() -> str:
    return _generate_reference("PO")

def generate_invoice_internal_reference() -> str:
    return _generate_reference("INV")
