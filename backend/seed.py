"""
seed.py
=======
Seeds the database with initial Module 1 data:
  - 4 Users (Admin, Procurement Officer, Vendor, Manager)
  - 5 Vendor Categories
  - 5 Vendors

Usage (inside docker):
  docker compose exec backend python seed.py
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorCategory, VendorStatus
from app.utils.security import hash_password


async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Starting seed process...")

        # ---------------------------------------------------------
        # 1. Vendor Categories
        # ---------------------------------------------------------
        categories_data = [
            {"name": "IT & Software", "description": "Software licenses, SaaS, and IT services"},
            {"name": "Hardware & Electronics", "description": "Laptops, servers, peripherals"},
            {"name": "Office Supplies", "description": "Stationery, pantry items, print supplies"},
            {"name": "Logistics & Transport", "description": "Courier, freight, and shipping services"},
            {"name": "Consulting Services", "description": "Legal, HR, and business consulting"},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat = VendorCategory(**cat_data)
            db.add(cat)
            categories.append(cat)
        
        await db.flush()
        print(f"Created {len(categories)} vendor categories.")

        # ---------------------------------------------------------
        # 2. Users (Without Vendor Links Initially)
        # ---------------------------------------------------------
        default_pwd = hash_password("Password@123")
        
        users_data = [
            {
                "email": "admin@vendorbridge.com",
                "hashed_password": default_pwd,
                "full_name": "System Admin",
                "role": UserRole.ADMIN,
                "phone": "+1-555-0001",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "officer@vendorbridge.com",
                "hashed_password": default_pwd,
                "full_name": "Procurement Officer",
                "role": UserRole.PROCUREMENT_OFFICER,
                "phone": "+1-555-0002",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "manager@vendorbridge.com",
                "hashed_password": default_pwd,
                "full_name": "Approval Manager",
                "role": UserRole.MANAGER,
                "phone": "+1-555-0003",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "vendor@techcorp.com",
                "hashed_password": default_pwd,
                "full_name": "Vendor Representative",
                "role": UserRole.VENDOR,
                "phone": "+1-555-0004",
                "is_active": True,
                "is_verified": True,
            }
        ]

        users = []
        for u_data in users_data:
            u = User(**u_data)
            db.add(u)
            users.append(u)
            
        await db.flush()
        print(f"Created {len(users)} users.")

        admin_user = next(u for u in users if u.role == UserRole.ADMIN)
        vendor_user = next(u for u in users if u.role == UserRole.VENDOR)

        # ---------------------------------------------------------
        # 3. Vendors
        # ---------------------------------------------------------
        vendors_data = [
            {
                "company_name": "TechCorp Solutions",
                "gst_number": "27AAPFT1234F1Z1",
                "pan_number": "AAPFT1234F",
                "category_id": categories[0].id,
                "contact_person": "Vendor Representative",
                "email": "vendor@techcorp.com",
                "phone": "+1-555-0004",
                "city": "New York",
                "country": "USA",
                "status": VendorStatus.ACTIVE,
                "created_by": admin_user.id,
            },
            {
                "company_name": "Global Hardware Dist.",
                "gst_number": "27AABCH5678H1Z2",
                "pan_number": "AABCH5678H",
                "category_id": categories[1].id,
                "contact_person": "Jane Smith",
                "email": "contact@globalhardware.com",
                "phone": "+1-555-1001",
                "city": "Austin",
                "country": "USA",
                "status": VendorStatus.ACTIVE,
                "created_by": admin_user.id,
            },
            {
                "company_name": "Stationery Central",
                "gst_number": "06AXYZS9012K1Z3",
                "pan_number": "AXYZS9012K",
                "category_id": categories[2].id,
                "contact_person": "Bob Jones",
                "email": "sales@stationerycentral.com",
                "phone": "+1-555-2002",
                "city": "Chicago",
                "country": "USA",
                "status": VendorStatus.PENDING,
                "created_by": admin_user.id,
            },
            {
                "company_name": "FastTrack Logistics",
                "gst_number": "07AAQPF3456L1Z4",
                "pan_number": "AAQPF3456L",
                "category_id": categories[3].id,
                "contact_person": "Alice Cooper",
                "email": "alice@fasttrack.com",
                "phone": "+1-555-3003",
                "city": "Los Angeles",
                "country": "USA",
                "status": VendorStatus.SUSPENDED,
                "created_by": admin_user.id,
            },
            {
                "company_name": "Expert Consults LLP",
                "gst_number": "29AABCU7890M1Z5",
                "pan_number": "AABCU7890M",
                "category_id": categories[4].id,
                "contact_person": "Charles Darwin",
                "email": "info@expertconsults.com",
                "phone": "+1-555-4004",
                "city": "Seattle",
                "country": "USA",
                "status": VendorStatus.ACTIVE,
                "created_by": admin_user.id,
            },
        ]

        vendors = []
        for v_data in vendors_data:
            v = Vendor(**v_data)
            db.add(v)
            vendors.append(v)
            
        await db.flush()
        print(f"Created {len(vendors)} vendors.")

        # Link the vendor user to the first vendor company
        vendor_user.vendor_company_id = vendors[0].id
        
        await db.commit()
        print("Seed data successfully committed!")


if __name__ == "__main__":
    asyncio.run(seed_data())
