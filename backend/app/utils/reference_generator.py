"""
Reference Number Generator
===========================
Utility for generating sequential reference numbers for
RFQs, Quotations, Purchase Orders, and Invoices.
"""

from datetime import datetime


def generate_rfq_number(sequence: int) -> str:
    """
    Generate a formatted RFQ reference number.
    Example: RFQ-2024-0001

    TODO: Implement with DB sequence or atomic counter.
    """
    year = datetime.utcnow().year
    return f"RFQ-{year}-{sequence:04d}"


def generate_quotation_number(sequence: int) -> str:
    """
    Generate a formatted Quotation reference number.
    Example: QUO-2024-0001

    TODO: Implement with DB sequence or atomic counter.
    """
    year = datetime.utcnow().year
    return f"QUO-{year}-{sequence:04d}"


def generate_po_number(sequence: int) -> str:
    """
    Generate a formatted Purchase Order number.
    Example: PO-2024-0001

    TODO: Implement with DB sequence or atomic counter.
    """
    year = datetime.utcnow().year
    return f"PO-{year}-{sequence:04d}"


def generate_invoice_internal_reference(sequence: int) -> str:
    """
    Generate an internal invoice reference number.
    Example: INV-2024-0001

    TODO: Implement with DB sequence or atomic counter.
    """
    year = datetime.utcnow().year
    return f"INV-{year}-{sequence:04d}"
