"""
services/email_service.py
=========================
SMTP Email Service for sending POs and Invoices.
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "test@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@vendorbridge.com")

async def _send_email(to_email: str, subject: str, body: str, pdf_path: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(body)

    # Attach PDF
    full_path = Path("/app") / pdf_path
    if full_path.exists():
        with open(full_path, "rb") as f:
            pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=full_path.name
            )

    try:
        # We use a synchronous SMTP block inside async, which is acceptable for this prototype
        # In a real async app, use aiosmtplib.
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            # server.starttls()
            # server.login(SMTP_USER, SMTP_PASSWORD)
            # server.send_message(msg)
            print(f"[EMAIL MOCK] Sent to {to_email}. Subject: {subject}. Attached: {pdf_path}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")

async def send_po_email(vendor_email: str, vendor_name: str, po_number: str, pdf_path: str):
    subject = f"VendorBridge: New Purchase Order {po_number}"
    body = f"Dear {vendor_name},\n\nPlease find attached the Purchase Order {po_number}.\n\nRegards,\nVendorBridge Team"
    await _send_email(vendor_email, subject, body, pdf_path)

async def send_invoice_email(vendor_email: str, vendor_name: str, invoice_number: str, pdf_path: str):
    subject = f"VendorBridge: Invoice {invoice_number} Generated"
    body = f"Dear {vendor_name},\n\nPlease find attached your generated Invoice {invoice_number}.\n\nRegards,\nVendorBridge Team"
    await _send_email(vendor_email, subject, body, pdf_path)
