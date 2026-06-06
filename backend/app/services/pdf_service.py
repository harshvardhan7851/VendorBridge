"""
PDF Service — stub methods only.
Generates PDF documents for Purchase Orders and Reports.
"""


class PDFService:
    """
    Generates PDF documents using a PDF library (e.g., ReportLab or WeasyPrint).

    TODO: Initialize PDF engine in __init__
    """

    async def generate_purchase_order_pdf(self, po_id: str) -> bytes:
        """
        Generate a PDF for the given Purchase Order.

        TODO:
          1. Fetch PO with all line items, vendor, and company details
          2. Load PO PDF template
          3. Render template with data
          4. Return PDF bytes
        """
        raise NotImplementedError

    async def generate_invoice_pdf(self, invoice_id: str) -> bytes:
        """
        Generate a PDF for the given Invoice.

        TODO:
          1. Fetch Invoice with PO and vendor details
          2. Render invoice template
          3. Return PDF bytes
        """
        raise NotImplementedError

    async def generate_spend_report_pdf(self, filters: dict) -> bytes:
        """
        Generate a spend analysis report PDF.

        TODO:
          1. Fetch aggregated spend data
          2. Render report template with charts/tables
          3. Return PDF bytes
        """
        raise NotImplementedError


# pdf_service = PDFService()
