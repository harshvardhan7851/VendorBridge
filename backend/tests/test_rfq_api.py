"""
tests/test_rfq_api.py
=====================
HTTP-level integration tests for the RFQ API (/api/v1/rfqs).

Strategy for DB isolation:
  - Each test overrides get_db with a session whose commit() is patched
    to flush() only — so service writes are visible within the test but
    the outer transaction is always rolled back at the end.

Run:
    docker compose exec backend python -m pytest tests/test_rfq_api.py -v
"""

import io
import uuid
import os
import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_db
from app.utils.security import create_access_token, hash_password
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.rfq import RFQ, RFQStatus, RFQLineItem, RFQVendorAssignment
from app.models.notification import Notification

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://vendorbridge:vendorbridge@postgres:5432/vendorbridge",
)


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _token(user: User, role: UserRole) -> str:
    return create_access_token(str(user.id), role.value)

def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

async def make_user(
    session: AsyncSession,
    role: UserRole,
    vendor_id=None,
) -> User:
    u = User(
        email=f"t_{uuid.uuid4().hex[:8]}@vb.test",
        hashed_password=hash_password("pw"),
        full_name="Test",
        role=role,
        vendor_company_id=vendor_id,
        is_active=True,
        is_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


async def make_vendor(session: AsyncSession) -> Vendor:
    v = Vendor(
        company_name=f"Corp {uuid.uuid4().hex[:6]}",
        status=VendorStatus.ACTIVE,
    )
    session.add(v)
    await session.flush()
    return v


async def make_rfq(
    session: AsyncSession,
    user: User,
    status: RFQStatus = RFQStatus.DRAFT,
) -> RFQ:
    r = RFQ(
        rfq_number=f"RFQ-{uuid.uuid4().hex[:8].upper()}",
        title="Test RFQ Title",
        description="Test description",
        status=status,
        deadline=datetime.now(timezone.utc) + timedelta(days=7),
        created_by=user.id,
        updated_by=user.id,
    )
    session.add(r)
    await session.flush()
    return r


async def make_line_item(session: AsyncSession, rfq: RFQ) -> RFQLineItem:
    li = RFQLineItem(
        rfq_id=rfq.id,
        product_name="Widget A",
        quantity=Decimal("10.00"),
        unit="pcs",
        updated_by=rfq.created_by,
    )
    session.add(li)
    await session.flush()
    return li


async def assign_vendor(session: AsyncSession, rfq: RFQ, vendor: Vendor):
    session.add(RFQVendorAssignment(
        rfq_id=rfq.id,
        vendor_id=vendor.id,
        status="INVITED",
    ))
    await session.flush()


# ---------------------------------------------------------------------------
# Core runner
# Key: patch session.commit → session.flush so service commits don't close
#      the outer transaction. We roll back everything at the end.
# ---------------------------------------------------------------------------

async def run(test_fn):
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async with factory() as session:
        async with session.begin():
            # Patch commit → flush (keeps transaction open for rollback)
            session.commit = session.flush  # type: ignore[method-assign]

            async def _override_db():
                yield session

            app.dependency_overrides[get_db] = _override_db

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                try:
                    await test_fn(client, session)
                finally:
                    app.dependency_overrides.pop(get_db, None)
                    await session.rollback()

    await engine.dispose()


# ===========================================================================
# 1. Auth guards
# ===========================================================================

@pytest.mark.asyncio
async def test_no_token_returns_403():
    async def _t(client, s):
        r = await client.post("/api/v1/rfqs/", json={"title": "X"})
        assert r.status_code == 403
    await run(_t)


@pytest.mark.asyncio
async def test_vendor_cannot_create_rfq():
    async def _t(client, s):
        vendor = await make_vendor(s)
        user = await make_user(s, UserRole.VENDOR, vendor_id=vendor.id)
        r = await client.post(
            "/api/v1/rfqs/",
            json={"title": "Nope"},
            headers=auth(_token(user, UserRole.VENDOR)),
        )
        assert r.status_code == 403
    await run(_t)


# ===========================================================================
# 2. Create RFQ
# ===========================================================================

@pytest.mark.asyncio
async def test_create_rfq_success():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        r = await client.post(
            "/api/v1/rfqs/",
            json={"title": "Office Supplies Q2", "description": "Pens and paper"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["status"] == "DRAFT"
        assert data["rfq_number"].startswith("RFQ-")
        assert data["created_by"] == str(officer.id)
    await run(_t)


# ===========================================================================
# 3. List RFQs
# ===========================================================================

@pytest.mark.asyncio
async def test_officer_sees_only_own_rfqs():
    async def _t(client, s):
        o1 = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        o2 = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq1 = await make_rfq(s, o1)
        await make_rfq(s, o2)

        r = await client.get("/api/v1/rfqs/", headers=auth(_token(o1, UserRole.PROCUREMENT_OFFICER)))
        assert r.status_code == 200
        items = r.json()["data"]["items"]
        ids = [i["id"] for i in items]
        assert str(rfq1.id) in ids
        for i in items:
            assert i["created_by"] == str(o1.id)
    await run(_t)


@pytest.mark.asyncio
async def test_manager_sees_all_rfqs():
    async def _t(client, s):
        o1 = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        o2 = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        mgr = await make_user(s, UserRole.MANAGER)
        rfq1 = await make_rfq(s, o1)
        rfq2 = await make_rfq(s, o2)

        r = await client.get("/api/v1/rfqs/", headers=auth(_token(mgr, UserRole.MANAGER)))
        ids = [i["id"] for i in r.json()["data"]["items"]]
        assert str(rfq1.id) in ids
        assert str(rfq2.id) in ids
    await run(_t)


@pytest.mark.asyncio
async def test_vendor_sees_only_assigned_rfqs():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        vuser = await make_user(s, UserRole.VENDOR, vendor_id=vendor.id)
        rfq_yes = await make_rfq(s, officer)
        rfq_no = await make_rfq(s, officer)
        await assign_vendor(s, rfq_yes, vendor)

        r = await client.get("/api/v1/rfqs/", headers=auth(_token(vuser, UserRole.VENDOR)))
        ids = [i["id"] for i in r.json()["data"]["items"]]
        assert str(rfq_yes.id) in ids
        assert str(rfq_no.id) not in ids
    await run(_t)


@pytest.mark.asyncio
async def test_status_filter():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        await make_rfq(s, officer, RFQStatus.DRAFT)
        sent = await make_rfq(s, officer, RFQStatus.SENT)

        r = await client.get(
            "/api/v1/rfqs/?status=SENT",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        ids = [i["id"] for i in r.json()["data"]["items"]]
        assert str(sent.id) in ids
        for i in r.json()["data"]["items"]:
            assert i["status"] == "SENT"
    await run(_t)


# ===========================================================================
# 4. Get detail
# ===========================================================================

@pytest.mark.asyncio
async def test_get_rfq_detail_with_line_items():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        await make_line_item(s, rfq)

        r = await client.get(
            f"/api/v1/rfqs/{rfq.id}",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["id"] == str(rfq.id)
        assert len(data["line_items"]) == 1
    await run(_t)


@pytest.mark.asyncio
async def test_get_rfq_404():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        r = await client.get(
            f"/api/v1/rfqs/{uuid.uuid4()}",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 404
    await run(_t)


@pytest.mark.asyncio
async def test_vendor_blocked_from_unassigned_rfq():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        vuser = await make_user(s, UserRole.VENDOR, vendor_id=vendor.id)
        rfq = await make_rfq(s, officer)

        r = await client.get(
            f"/api/v1/rfqs/{rfq.id}",
            headers=auth(_token(vuser, UserRole.VENDOR)),
        )
        assert r.status_code == 403
    await run(_t)


# ===========================================================================
# 5. Update RFQ
# ===========================================================================

@pytest.mark.asyncio
async def test_update_draft_rfq():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)

        r = await client.put(
            f"/api/v1/rfqs/{rfq.id}",
            json={"title": "Updated Title"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert r.json()["data"]["title"] == "Updated Title"
    await run(_t)


@pytest.mark.asyncio
async def test_update_sent_rfq_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer, RFQStatus.SENT)

        r = await client.put(
            f"/api/v1/rfqs/{rfq.id}",
            json={"title": "Should Fail"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
    await run(_t)


# ===========================================================================
# 6. Close RFQ
# ===========================================================================

@pytest.mark.asyncio
async def test_close_rfq():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)

        r = await client.patch(
            f"/api/v1/rfqs/{rfq.id}/close",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "CLOSED"
    await run(_t)


@pytest.mark.asyncio
async def test_close_already_closed_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer, RFQStatus.CLOSED)

        r = await client.patch(
            f"/api/v1/rfqs/{rfq.id}/close",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
    await run(_t)


# ===========================================================================
# 7. Line Items
# ===========================================================================

@pytest.mark.asyncio
async def test_add_line_item():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/line-items",
            json={"product_name": "Paper", "quantity": "100", "unit": "reams"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 201
        assert r.json()["data"]["product_name"] == "Paper"
    await run(_t)


@pytest.mark.asyncio
async def test_add_line_item_to_sent_rfq_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer, RFQStatus.SENT)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/line-items",
            json={"product_name": "Pen", "quantity": "50"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
    await run(_t)


@pytest.mark.asyncio
async def test_list_line_items():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        await make_line_item(s, rfq)
        await make_line_item(s, rfq)

        r = await client.get(
            f"/api/v1/rfqs/{rfq.id}/line-items",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2
    await run(_t)


@pytest.mark.asyncio
async def test_update_line_item():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        item = await make_line_item(s, rfq)

        r = await client.put(
            f"/api/v1/rfqs/line-items/{item.id}",
            json={"product_name": "Renamed", "quantity": "5"},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert r.json()["data"]["product_name"] == "Renamed"
    await run(_t)


@pytest.mark.asyncio
async def test_delete_line_item():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        item = await make_line_item(s, rfq)

        r = await client.delete(
            f"/api/v1/rfqs/line-items/{item.id}",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 204

        gone = await s.execute(select(RFQLineItem).where(RFQLineItem.id == item.id))
        assert gone.scalar_one_or_none() is None
    await run(_t)


# ===========================================================================
# 8. Vendor Assignment
# ===========================================================================

@pytest.mark.asyncio
async def test_assign_vendors():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        v1 = await make_vendor(s)
        v2 = await make_vendor(s)
        rfq = await make_rfq(s, officer)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/assign-vendors",
            json={"vendor_ids": [str(v1.id), str(v2.id)]},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2
    await run(_t)


@pytest.mark.asyncio
async def test_assign_duplicate_vendor_skipped():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        rfq = await make_rfq(s, officer)

        for _ in range(2):
            r = await client.post(
                f"/api/v1/rfqs/{rfq.id}/assign-vendors",
                json={"vendor_ids": [str(vendor.id)]},
                headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
            )
            assert r.status_code == 200

        assert len(r.json()["data"]) == 1
    await run(_t)


@pytest.mark.asyncio
async def test_assign_nonexistent_vendor_404():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/assign-vendors",
            json={"vendor_ids": [str(uuid.uuid4())]},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 404
    await run(_t)


@pytest.mark.asyncio
async def test_list_assigned_vendors():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        rfq = await make_rfq(s, officer)
        await assign_vendor(s, rfq, vendor)

        r = await client.get(
            f"/api/v1/rfqs/{rfq.id}/assigned-vendors",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data) == 1
        assert data[0]["vendor_name"] == vendor.company_name
    await run(_t)


# ===========================================================================
# 9. Attachments
# ===========================================================================

@pytest.mark.asyncio
async def test_upload_attachment():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        content = b"spec sheet content"

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/attachments",
            files={"file": ("spec.txt", io.BytesIO(content), "text/plain")},
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["filename"] == "spec.txt"
        assert data["file_size"] == len(content)
        assert str(rfq.id) in data["file_path"]
    await run(_t)


@pytest.mark.asyncio
async def test_list_attachments():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)

        for name in ["a.pdf", "b.pdf"]:
            await client.post(
                f"/api/v1/rfqs/{rfq.id}/attachments",
                files={"file": (name, io.BytesIO(b"data"), "application/pdf")},
                headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
            )

        r = await client.get(
            f"/api/v1/rfqs/{rfq.id}/attachments",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert len(r.json()["data"]) == 2
    await run(_t)


# ===========================================================================
# 10. Send RFQ
# ===========================================================================

@pytest.mark.asyncio
async def test_send_without_line_items_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        rfq = await make_rfq(s, officer)
        await assign_vendor(s, rfq, vendor)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/send",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
        assert "line item" in r.json()["detail"].lower()
    await run(_t)


@pytest.mark.asyncio
async def test_send_without_vendors_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer)
        await make_line_item(s, rfq)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/send",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
        assert "vendor" in r.json()["detail"].lower()
    await run(_t)


@pytest.mark.asyncio
async def test_send_rfq_success_creates_notification():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        vendor = await make_vendor(s)
        vuser = await make_user(s, UserRole.VENDOR, vendor_id=vendor.id)

        rfq = await make_rfq(s, officer)
        await make_line_item(s, rfq)
        await assign_vendor(s, rfq, vendor)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/send",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "SENT"

        # Notification must exist for the vendor user
        result = await s.execute(
            select(Notification).where(
                Notification.user_id == vuser.id,
                Notification.entity_id == rfq.id,
            )
        )
        notif = result.scalar_one_or_none()
        assert notif is not None
        assert notif.type.value == "RFQ_INVITE"
        assert rfq.title in notif.message
        assert notif.is_read is False
    await run(_t)


@pytest.mark.asyncio
async def test_send_already_sent_rfq_rejected():
    async def _t(client, s):
        officer = await make_user(s, UserRole.PROCUREMENT_OFFICER)
        rfq = await make_rfq(s, officer, RFQStatus.SENT)

        r = await client.post(
            f"/api/v1/rfqs/{rfq.id}/send",
            headers=auth(_token(officer, UserRole.PROCUREMENT_OFFICER)),
        )
        assert r.status_code == 422
    await run(_t)
