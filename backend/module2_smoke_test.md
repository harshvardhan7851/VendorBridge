# Module 2 Smoke Test Checklist

This checklist describes the end-to-end integration test flow for RFQ Management, Quotations, and Winner Selection.

## 1. Procurement Officer Actions (Create & Send RFQ)
- [ ] Login as a Procurement Officer.
- [ ] `POST /api/v1/rfqs/` - Create a new RFQ (status becomes `DRAFT`).
- [ ] `POST /api/v1/rfqs/{rfq_id}/line-items` - Add one or more line items to the RFQ.
- [ ] `POST /api/v1/rfqs/{rfq_id}/assign-vendors` - Assign vendors to the RFQ (status for each vendor becomes `INVITED`).
- [ ] `POST /api/v1/rfqs/{rfq_id}/send` - Send the RFQ. 
  - Validates line items and vendors exist.
  - Updates RFQ status to `SENT`.
  - Creates `RFQ_INVITE` notification for the assigned vendor users.

## 2. Vendor Actions (View & Quote)
- [ ] Login as an invited Vendor user.
- [ ] `GET /api/v1/notifications/` - Vendor sees the `RFQ_INVITE` notification.
- [ ] `POST /api/v1/quotations/` - Vendor creates a draft quotation for the assigned RFQ, submitting prices for the line items (status becomes `DRAFT`).
- [ ] `POST /api/v1/quotations/{quotation_id}/submit` - Vendor submits the quotation (status becomes `SUBMITTED`).
  - Creates `QUOTATION_RECEIVED` notification for the Procurement Officer.

## 3. Comparison & Winner Selection
- [ ] Login as Procurement Officer.
- [ ] `GET /api/v1/notifications/` - Officer sees the `QUOTATION_RECEIVED` notification.
- [ ] `GET /api/v1/comparison/rfq/{rfq_id}` - Officer views the comparison engine.
  - Verifies submitted quotations are sorted by `total_amount` ASC.
  - Verifies `is_lowest_price` flag is correctly set on line items.
  - Verifies `is_lowest_total` flag is correctly set on the best overall quotation.
- [ ] `POST /api/v1/quotations/{quotation_id}/select-winner` - Officer selects a winning quotation.
  - Sets the winner quotation status to `SELECTED`.
  - Rejects all other quotations for the RFQ.
  - Sets the RFQ status to `CLOSED`.
  - Creates `WINNER_SELECTED` notification for the winning vendor.
  - **Module 3 Prep:** Verifies a new record is created in the `approval_triggers` table for the winning quotation.
