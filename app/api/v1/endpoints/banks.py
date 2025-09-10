from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.services.bank_service import BankService
from app.schemas.bank import Bank, BankList, BankDetail
from app.utils.pagination import PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[BankList])
async def get_banks(
    q: Optional[str] = Query(None, description="Search in bank name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all banks with branch counts"""
    banks_with_counts = await BankService.get_all_banks(db)
    
    # Apply search filter if provided
    if q:
        filtered_banks = []
        for bank, branch_count in banks_with_counts:
            if q.upper() in bank.name.upper():
                filtered_banks.append((bank, branch_count))
        banks_with_counts = filtered_banks
    
    # Apply pagination
    total = len(banks_with_counts)
    paginated_banks = banks_with_counts[skip:skip + limit]
    
    result = []
    for bank, branch_count in paginated_banks:
        result.append(BankList(
            id=bank.id,
            name=bank.name,
            branch_count=branch_count
        ))
    
    return PaginatedResponse(
        items=result,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{bank_id}", response_model=BankDetail)
async def get_bank(bank_id: int, db: AsyncSession = Depends(get_db)):
    """Get bank by ID with branches"""
    bank = await BankService.get_bank_by_id(db, bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank
