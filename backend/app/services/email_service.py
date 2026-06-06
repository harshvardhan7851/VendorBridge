"""
Email Service — stub methods only.
Handles all outbound email communications via SMTP.
"""


class EmailService:
    """
    Responsible for sending transactional emails.
    Uses SMTP settings from app.core.config.settings.

    TODO: Initialize SMTP client in __init__
    """

    async def send_welcome_email(self, to_email: str, full_name: str):
        # TODO: Load welcome email template, send via SMTP
        raise NotImplementedError

    async def send_verification_email(self, to_email: str, token: str):
        # TODO: Build verification URL with token, send email
        raise NotImplementedError

    async def send_password_reset_email(self, to_email: str, reset_token: str):
        # TODO: Build reset URL, load template, send email
        raise NotImplementedError

    async def send_rfq_invitation(self, vendor_email: str, rfq_number: str, deadline: str):
        # TODO: Notify vendor of new RFQ invitation with deadline
        raise NotImplementedError

    async def send_po_notification(self, vendor_email: str, po_number: str):
        # TODO: Notify vendor that a PO has been issued
        raise NotImplementedError

    async def send_invoice_status_email(self, vendor_email: str, invoice_number: str, status: str):
        # TODO: Notify vendor of invoice approval or rejection
        raise NotImplementedError

    async def send_approval_required_email(self, approver_email: str, entity_type: str, entity_id: str):
        # TODO: Notify manager/admin that approval is required
        raise NotImplementedError


# Module-level singleton (instantiated when SMTP config is available)
# email_service = EmailService()
