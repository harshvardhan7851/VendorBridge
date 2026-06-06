"""
Vendor Model
============
Represents a registered vendor/supplier in the system.

Future Relationships:
  - Vendor has many Users as contacts (via vendor_id FK on User)
  - Vendor has many RFQs (via many-to-many: rfq_vendors association table)
  - Vendor has many Quotations (via vendor_id FK on Quotation)
  - Vendor has many Invoices (via vendor_id FK on Invoice)
"""

import uuid
from sqlalchemy import Column, String, Text, Enum as SAEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    # --- Primary Key ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Business Identity ---
    company_name = Column(String(255), nullable=False, unique=True)
    registration_number = Column(String(100), nullable=True, unique=True)
    tax_id = Column(String(100), nullable=True)

    # --- Contact Information ---
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)

    # --- Address ---
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # --- Status ---
    status = Column(
        SAEnum("pending", "approved", "rejected", "suspended", name="vendor_status"),
        nullable=False,
        default="pending",
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # --- Additional Info ---
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)   # e.g., "IT", "Logistics", "Office Supplies"

    # --- Timestamps ---
    # TODO: Add created_at, updated_at via TimestampMixin

    # --- Future Relationships ---
    # TODO: contacts = relationship("User", back_populates="vendor")
    # TODO: rfqs = relationship("RFQ", secondary="rfq_vendors", back_populates="vendors")
    # TODO: quotations = relationship("Quotation", back_populates="vendor")
    # TODO: invoices = relationship("Invoice", back_populates="vendor")

    def __repr__(self) -> str:
        return f"<Vendor id={self.id} company={self.company_name} status={self.status}>"
