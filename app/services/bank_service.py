from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.bank import Bank
from app.models.branch import Branch
from app.schemas.bank import BankCreate

class BankService:
    @staticmethod
    async def get_all_banks(db: AsyncSession) -> List[Bank]:
        """Get all banks with branch count"""
        result = await db.execute(
            select(Bank, func.count(Branch.ifsc).label('branch_count'))
            .outerjoin(Branch, Bank.id == Branch.bank_id)
            .group_by(Bank.id, Bank.name)
            .order_by(Bank.name)
        )
        return result.all()
    
    @staticmethod
    async def get_bank_by_id(db: AsyncSession, bank_id: int) -> Optional[Bank]:
        """Get bank by ID with branches"""
        result = await db.execute(
            select(Bank)
            .options(selectinload(Bank.branches))
            .where(Bank.id == bank_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_bank_count(db: AsyncSession) -> int:
        """Get total number of banks"""
        result = await db.execute(select(func.count(Bank.id)))
        return result.scalar()
    
    @staticmethod
    async def create_bank(db: AsyncSession, bank: BankCreate) -> Bank:
        """Create a new bank"""
        db_bank = Bank(id=bank.id, name=bank.name)
        db.add(db_bank)
        await db.commit()
        await db.refresh(db_bank)
        return db_bank
