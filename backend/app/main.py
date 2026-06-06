"""
VendorBridge ERP - FastAPI Application Entry Point
===================================================
This is the root application file. It:
  - Creates the FastAPI app instance
  - Registers all routers
  - Configures CORS middleware
  - Sets up startup/shutdown lifecycle events
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Router Imports
# ---------------------------------------------------------------------------
from app.routers import (
    auth,
    vendors,
    vendor_categories,
    rfqs,
    quotations,
    approvals,
    purchase_orders,
    invoices,
    notifications,
    reports,
    comparison,
    activity_logs,
)

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VendorBridge ERP API",
    description=(
        "Procurement & Vendor Management ERP — "
        "Skeleton API. Endpoints return placeholder responses."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS Middleware
# TODO: Restrict origins to FRONTEND_URL in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Replace with [settings.FRONTEND_URL] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router Registration
# All routers are prefixed with /api/v1
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(auth.router,           prefix=f"{API_PREFIX}/auth",           tags=["Authentication"])
app.include_router(vendor_categories.router, prefix=f"{API_PREFIX}/vendor-categories", tags=["Vendor Categories"])
app.include_router(vendors.router,        prefix=f"{API_PREFIX}/vendors",        tags=["Vendors"])
app.include_router(rfqs.router,           prefix=f"{API_PREFIX}/rfqs",           tags=["RFQs"])
app.include_router(quotations.router,     prefix=f"{API_PREFIX}/quotations",     tags=["Quotations"])
app.include_router(approvals.router,      prefix=f"{API_PREFIX}/approvals",      tags=["Approvals"])
app.include_router(purchase_orders.router,prefix=f"{API_PREFIX}/purchase-orders",tags=["Purchase Orders"])
app.include_router(invoices.router,       prefix=f"{API_PREFIX}/invoices",       tags=["Invoices"])
app.include_router(notifications.router,  prefix=f"{API_PREFIX}/notifications",  tags=["Notifications"])
app.include_router(activity_logs.router,  prefix=f"{API_PREFIX}/activity-logs",  tags=["Activity Logs"])
app.include_router(reports.router,        prefix=f"{API_PREFIX}/reports",        tags=["Reports"])
app.include_router(comparison.router,     prefix=f"{API_PREFIX}/comparison",     tags=["Comparison Engine"])

# ---------------------------------------------------------------------------
# Lifecycle Events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    TODO: Initialize database connection pool, run startup checks.
    """
    print("🚀 VendorBridge API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """
    TODO: Close database connections, cleanup resources.
    """
    print("🛑 VendorBridge API shutting down...")


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint.
    Used by Docker, load balancers, and monitoring tools.
    """
    return {"status": "ok", "service": "vendorbridge-api", "version": "0.1.0"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to VendorBridge ERP API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
