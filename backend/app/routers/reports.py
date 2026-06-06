"""
routers/reports.py
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.middlewares.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.report import ProcurementSummaryResponse, VendorPerformanceResponse, MonthlySpendResponse
from app.services.report_service import ReportService

router = APIRouter()

def _ok(data=None, message=""):
    return {"success": True, "data": data, "message": message}

@router.get("/procurement-summary", response_model=dict)
async def get_procurement_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER))
):
    service = ReportService(db)
    summary = await service.get_procurement_summary()
    return _ok(ProcurementSummaryResponse.model_validate(summary).model_dump())

@router.get("/vendor-performance", response_model=dict)
async def get_vendor_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.MANAGER))
):
    service = ReportService(db)
    perf = await service.get_vendor_performance()
    data = [VendorPerformanceResponse.model_validate(p).model_dump() for p in perf]
    return _ok(data)

@router.get("/monthly-spend", response_model=dict)
async def get_monthly_spend(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.PROCUREMENT_OFFICER, UserRole.MANAGER))
):
    service = ReportService(db)
    spend = await service.get_monthly_spend()
    data = [MonthlySpendResponse.model_validate(s).model_dump() for s in spend]
    return _ok(data)

@router.get("/export/vendors")
async def export_vendors(
    db: AsyncSession = Depends(get_db),
    # Note: the problem states Admin only, but require_roles inherently allows Admin.
    # We will enforce MANAGER here, which admin can bypass, or we just put no roles if we want purely Admin. 
    # Let's put a dummy role that nobody has except ADMIN, or just rely on Admin bypass.
    # We'll just put no roles except ADMIN
    current_user: User = Depends(require_roles()) # Empty means Admin only due to the bypass
):
    service = ReportService(db)
    csv_data = await service.export_vendors_csv()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"vendors_export_{date_str}.csv"
    
    # We yield the string encoded
    async def iterfile():
        yield csv_data.encode('utf-8')
        
    return StreamingResponse(
        iterfile(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/procurement")
async def export_procurement(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles()) # Admin only
):
    service = ReportService(db)
    csv_data = await service.export_procurement_csv()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"procurement_export_{date_str}.csv"
    
    async def iterfile():
        yield csv_data.encode('utf-8')
        
    return StreamingResponse(
        iterfile(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
