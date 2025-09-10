from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.branch_service import BranchService
from app.schemas.branch import Branch, BranchDetail
from app.utils.pagination import PaginatedResponse

router = APIRouter()

@router.get("/{ifsc}", response_model=BranchDetail)
async def get_branch_by_ifsc(ifsc: str, db: AsyncSession = Depends(get_db)):
    """Get branch details by IFSC code"""
    branch = await BranchService.get_branch_by_ifsc(db, ifsc)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.get("/", response_model=PaginatedResponse[Branch])
async def search_branches(
    q: Optional[str] = Query(None, description="Search in IFSC, branch name, address, or bank name"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    bank_id: Optional[int] = Query(None, description="Filter by bank ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Search branches with multiple filters"""
    branches, total = await BranchService.search_branches(
        db, 
        query=q, 
        city=city, 
        state=state, 
        district=district, 
        bank_id=bank_id,
        skip=skip, 
        limit=limit
    )
    return PaginatedResponse(
        items=branches,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/bank/{bank_id}", response_model=PaginatedResponse[Branch])
async def get_branches_by_bank(
    bank_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all branches for a specific bank"""
    branches, total = await BranchService.get_branches_by_bank_id(db, bank_id, skip, limit)
    if not branches:
        raise HTTPException(status_code=404, detail="Bank not found or no branches found")
    return PaginatedResponse(
        items=branches,
        total=total,
        skip=skip,
        limit=limit
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No branches found for this bank")
    return branches
