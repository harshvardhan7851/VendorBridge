"""
Approvals Router — Placeholder endpoints.
"""
from uuid import UUID
from fastapi import APIRouter

router = APIRouter()
NOT_IMPLEMENTED = {"message": "Not Implemented"}


@router.get("/", summary="List Approval Requests")
async def list_approvals():
    # TODO: Return approvals assigned to current manager/admin
    return NOT_IMPLEMENTED


@router.get("/{approval_id}", summary="Get Approval Request")
async def get_approval(approval_id: UUID):
    return NOT_IMPLEMENTED


@router.post("/{approval_id}/approve", summary="Approve Request")
async def approve_request(approval_id: UUID):
    # TODO: Set status="approved", trigger next workflow step
    return NOT_IMPLEMENTED


@router.post("/{approval_id}/reject", summary="Reject Request")
async def reject_request(approval_id: UUID):
    # TODO: Set status="rejected", notify requester
    return NOT_IMPLEMENTED
