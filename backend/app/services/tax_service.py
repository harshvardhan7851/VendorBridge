"""
services/tax_service.py
=======================
Reusable tax calculation service.
"""

import os
from decimal import Decimal

TAX_RATE_CGST = Decimal("9.0")
TAX_RATE_SGST = Decimal("9.0")
TAX_RATE_IGST = Decimal("18.0")

def calculate_taxes(subtotal: Decimal) -> dict:
    is_interstate = os.getenv("TAX_INTERSTATE", "false").lower() == "true"
    
    if is_interstate:
        igst = (subtotal * TAX_RATE_IGST) / Decimal("100")
        cgst = Decimal("0")
        sgst = Decimal("0")
        tax_amount = igst
    else:
        cgst = (subtotal * TAX_RATE_CGST) / Decimal("100")
        sgst = (subtotal * TAX_RATE_SGST) / Decimal("100")
        igst = Decimal("0")
        tax_amount = cgst + sgst
        
    grand_total = subtotal + tax_amount
    
    return {
        "cgst": cgst.quantize(Decimal("0.01")),
        "sgst": sgst.quantize(Decimal("0.01")),
        "igst": igst.quantize(Decimal("0.01")),
        "tax_amount": tax_amount.quantize(Decimal("0.01")),
        "grand_total": grand_total.quantize(Decimal("0.01")),
    }
