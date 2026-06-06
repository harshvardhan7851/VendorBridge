"""
services/comparison_service.py
==============================
Business logic for comparing quotations of an RFQ.
"""

import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quotation import Quotation, QuotationStatus
from app.models.rfq import RFQ
from app.schemas.quotation import QuotationDetail, QuotationLineItemResponse
from app.schemas.rfq import RFQDetail

class ComparisonService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rfq_comparison(self, rfq_id: uuid.UUID) -> dict:
        # Fetch RFQ
        rfq_result = await self.db.execute(
            select(RFQ)
            .options(
                selectinload(RFQ.line_items),
                selectinload(RFQ.vendor_assignments),
                selectinload(RFQ.attachments)
            )
            .where(RFQ.id == rfq_id)
        )
        rfq = rfq_result.scalar_one_or_none()
        if not rfq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found.")

        # Fetch SUBMITTED quotations for RFQ
        quotes_result = await self.db.execute(
            select(Quotation)
            .options(
                selectinload(Quotation.line_items),
                selectinload(Quotation.vendor)
            )
            .where(Quotation.rfq_id == rfq_id)
            .where(Quotation.status == QuotationStatus.SUBMITTED)
            .order_by(Quotation.total_amount.asc())
        )
        quotations = list(quotes_result.scalars().all())

        # Determine lowest overall total_amount
        lowest_total_id = None
        if quotations:
            # Sorted by total_amount ASC, so first one is lowest
            lowest_total_id = quotations[0].id

        # Determine lowest unit_price for each rfq_line_item
        lowest_prices = {}  # {rfq_line_item_id: lowest_price}
        lowest_price_quotation_line_items = set() # set of QuotationLineItem IDs that have lowest price

        for q in quotations:
            for li in q.line_items:
                if li.rfq_line_item_id:
                    current_lowest = lowest_prices.get(li.rfq_line_item_id)
                    if current_lowest is None or li.unit_price < current_lowest:
                        lowest_prices[li.rfq_line_item_id] = li.unit_price

        # Second pass to mark all line items matching lowest price
        for q in quotations:
            for li in q.line_items:
                if li.rfq_line_item_id and li.unit_price == lowest_prices.get(li.rfq_line_item_id):
                    lowest_price_quotation_line_items.add(li.id)

        # Build Response
        rfq_data = RFQDetail.model_validate(rfq).model_dump(mode="json")
        quotations_data = []
        for q in quotations:
            q_schema = QuotationDetail.model_validate(q)
            q_schema.is_lowest_total = (q.id == lowest_total_id)
            q_schema.vendor_name = q.vendor.company_name if q.vendor else None
            
            for li_schema in q_schema.line_items:
                li_schema.is_lowest_price = (li_schema.id in lowest_price_quotation_line_items)

            quotations_data.append(q_schema.model_dump(mode="json"))

        return {
            "rfq": rfq_data,
            "quotations": quotations_data
        }
