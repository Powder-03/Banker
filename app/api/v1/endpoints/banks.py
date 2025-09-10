from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.services.bank_service import BankService
from app.schemas.bank import Bank, BankList

router = APIRouter()

@router.get("/", response_model=List[BankList])
async def get_banks(db: AsyncSession = Depends(get_db)):
    """Get all banks with branch counts"""
    banks_with_counts = await BankService.get_all_banks(db)
    
    result = []
    for bank, branch_count in banks_with_counts:
        result.append(BankList(
            id=bank.id,
            name=bank.name,
            branch_count=branch_count
        ))
    
    return result

@router.get("/{bank_id}", response_model=Bank)
async def get_bank(bank_id: int, db: AsyncSession = Depends(get_db)):
    """Get bank by ID"""
    bank = await BankService.get_bank_by_id(db, bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank
    return bank
