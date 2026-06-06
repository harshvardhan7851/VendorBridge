"""
tests/test_module2_models.py
============================
Smoke tests for Module 2 ORM models.

Validates:
  1. All 7 tables exist in the DB.
  2. All 4 enum types exist in the DB.
  3. CRUD round-trips for each model.
  4. Unique constraint on rfq_vendor_assignments(rfq_id, vendor_id).
  5. CASCADE deletes propagate correctly.

Run inside Docker:
    docker compose exec backend python -m pytest tests/test_module2_models.py -v
"""

import uuid
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os

from app.models import (
    User, UserRole,
    Vendor, VendorStatus,
    RFQ, RFQStatus,
    RFQLineItem,
    RFQVendorAssignment, AssignmentStatus,
    RFQAttachment,
    Quotation, QuotationStatus,
    QuotationLineItem,
    Notification, NotificationType,
)

# ---------------------------------------------------------------------------
# Engine & Session scoped to the function (one event loop per test)
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://vendorbridge:vendorbridge@postgres:5432/vendorbridge",
)


async def _make_session() -> AsyncSession:
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    return factory(), engine


# ---------------------------------------------------------------------------
# Helper: run a test inside a rolled-back transaction
# ---------------------------------------------------------------------------

async def _run(coro):
    """Execute coro(session) inside a savepoint that is always rolled back."""
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory() as session:
        async with session.begin():
            try:
                await coro(session)
            finally:
                await session.rollback()
    await engine.dispose()


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

async def _seed_user(session: AsyncSession) -> User:
    user = User(
        email=f"test_{uuid.uuid4().hex[:8]}@vendorbridge.test",
        hashed_password="hashed_pw",
        full_name="Test User",
        role=UserRole.PROCUREMENT_OFFICER,
    )
    session.add(user)
    await session.flush()
    return user


async def _seed_vendor(session: AsyncSession) -> Vendor:
    vendor = Vendor(
        company_name=f"Acme Corp {uuid.uuid4().hex[:6]}",
        status=VendorStatus.ACTIVE,
    )
    session.add(vendor)
    await session.flush()
    return vendor


async def _seed_rfq(session: AsyncSession, user: User) -> RFQ:
    rfq = RFQ(
        rfq_number=f"RFQ-{uuid.uuid4().hex[:8].upper()}",
        title="Office Supplies Q1",
        description="Request for stationery and printer paper",
        status=RFQStatus.DRAFT,
        deadline=datetime.now(timezone.utc) + timedelta(days=7),
        created_by=user.id,
    )
    session.add(rfq)
    await session.flush()
    return rfq


# ---------------------------------------------------------------------------
# Test 1: All Module 2 tables exist
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_all_module2_tables_exist():
    async def _test(session: AsyncSession):
        expected = {
            "rfqs", "rfq_line_items", "rfq_vendor_assignments",
            "rfq_attachments", "quotations", "quotation_line_items", "notifications",
        }
        result = await session.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        )
        actual = {row[0] for row in result.fetchall()}
        missing = expected - actual
        assert not missing, f"Missing tables: {missing}"

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 2: All Module 2 enum types exist
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_all_module2_enum_types_exist():
    async def _test(session: AsyncSession):
        expected = {"rfqstatus", "assignmentstatus", "quotationstatus", "notificationtype"}
        result = await session.execute(
            text("SELECT typname FROM pg_type WHERE typcategory = 'E'")
        )
        actual = {row[0] for row in result.fetchall()}
        missing = expected - actual
        assert not missing, f"Missing enum types: {missing}"

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 3: RFQ CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_create_and_read():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        rfq = await _seed_rfq(session, user)

        result = await session.execute(select(RFQ).where(RFQ.id == rfq.id))
        fetched = result.scalar_one()

        assert fetched.title == "Office Supplies Q1"
        assert fetched.status == RFQStatus.DRAFT
        assert fetched.rfq_number.startswith("RFQ-")
        assert fetched.created_at is not None
        assert fetched.updated_at is not None

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 4: RFQLineItem CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_line_item_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        rfq = await _seed_rfq(session, user)

        item = RFQLineItem(
            rfq_id=rfq.id,
            product_name="A4 Paper Ream",
            quantity=Decimal("50.00"),
            unit="reams",
        )
        session.add(item)
        await session.flush()

        result = await session.execute(
            select(RFQLineItem).where(RFQLineItem.rfq_id == rfq.id)
        )
        fetched = result.scalar_one()
        assert fetched.product_name == "A4 Paper Ream"
        assert fetched.quantity == Decimal("50.00")

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 5: RFQVendorAssignment — create
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_vendor_assignment_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        vendor = await _seed_vendor(session)
        rfq = await _seed_rfq(session, user)

        assignment = RFQVendorAssignment(
            rfq_id=rfq.id,
            vendor_id=vendor.id,
            status=AssignmentStatus.INVITED,
        )
        session.add(assignment)
        await session.flush()
        assert assignment.id is not None
        assert assignment.status == AssignmentStatus.INVITED

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 6: RFQVendorAssignment — unique constraint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_vendor_assignment_unique_constraint():
    from sqlalchemy.exc import IntegrityError

    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        vendor = await _seed_vendor(session)
        rfq = await _seed_rfq(session, user)

        session.add(RFQVendorAssignment(
            rfq_id=rfq.id, vendor_id=vendor.id, status=AssignmentStatus.INVITED
        ))
        await session.flush()

        session.add(RFQVendorAssignment(
            rfq_id=rfq.id, vendor_id=vendor.id, status=AssignmentStatus.INVITED
        ))
        with pytest.raises(IntegrityError):
            await session.flush()

    # This test expects an error so we can't use _run (which calls rollback on the outer txn)
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with factory() as session:
        try:
            await _test(session)
        finally:
            await session.rollback()
    await engine.dispose()


# ---------------------------------------------------------------------------
# Test 7: RFQAttachment
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_attachment_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        rfq = await _seed_rfq(session, user)

        attachment = RFQAttachment(
            rfq_id=rfq.id,
            uploaded_by=user.id,
            filename="spec_sheet.pdf",
            file_path="/uploads/rfqs/spec_sheet.pdf",
            file_size=204800,
        )
        session.add(attachment)
        await session.flush()
        assert attachment.id is not None
        assert attachment.filename == "spec_sheet.pdf"
        assert attachment.file_size == 204800

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 8: Quotation CRUD
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quotation_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        vendor = await _seed_vendor(session)
        rfq = await _seed_rfq(session, user)

        quotation = Quotation(
            quotation_number=f"QUO-{uuid.uuid4().hex[:8].upper()}",
            rfq_id=rfq.id,
            vendor_id=vendor.id,
            status=QuotationStatus.DRAFT,
            delivery_days=14,
            total_amount=Decimal("12500.00"),
            notes="Includes free delivery over ₹10,000",
        )
        session.add(quotation)
        await session.flush()
        assert quotation.id is not None
        assert quotation.total_amount == Decimal("12500.00")
        assert quotation.status == QuotationStatus.DRAFT

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 9: QuotationLineItem
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quotation_line_item_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        vendor = await _seed_vendor(session)
        rfq = await _seed_rfq(session, user)

        quotation = Quotation(
            quotation_number=f"QUO-{uuid.uuid4().hex[:8].upper()}",
            rfq_id=rfq.id,
            vendor_id=vendor.id,
            status=QuotationStatus.SUBMITTED,
            total_amount=Decimal("5000.00"),
        )
        session.add(quotation)
        await session.flush()

        line = QuotationLineItem(
            quotation_id=quotation.id,
            unit_price=Decimal("100.00"),
            quantity=Decimal("50.00"),
            total_price=Decimal("5000.00"),
            notes="Standard grade",
        )
        session.add(line)
        await session.flush()
        assert line.id is not None
        assert line.total_price == Decimal("5000.00")

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 10: Notification
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_notification_create():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        rfq_id = uuid.uuid4()  # reference only, no actual RFQ needed

        notif = Notification(
            user_id=user.id,
            type=NotificationType.RFQ_INVITE,
            message="You have been invited to quote on RFQ-2024-001.",
            entity_type="rfq",
            entity_id=rfq_id,
        )
        session.add(notif)
        await session.flush()
        assert notif.id is not None
        assert notif.is_read is False       # default
        assert notif.type == NotificationType.RFQ_INVITE

    await _run(_test)


# ---------------------------------------------------------------------------
# Test 11: CASCADE delete — deleting RFQ removes line items
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rfq_cascade_delete_line_items():
    async def _test(session: AsyncSession):
        user = await _seed_user(session)
        rfq = await _seed_rfq(session, user)

        item = RFQLineItem(rfq_id=rfq.id, product_name="Pen", quantity=Decimal("100"))
        session.add(item)
        await session.flush()
        item_id = item.id

        await session.delete(rfq)
        await session.flush()

        result = await session.execute(select(RFQLineItem).where(RFQLineItem.id == item_id))
        assert result.scalar_one_or_none() is None, "Line item should be CASCADE deleted"

    await _run(_test)
