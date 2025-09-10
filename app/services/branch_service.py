from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional, Tuple
from app.models.branch import Branch
from app.models.bank import Bank
from app.schemas.branch import BranchCreate

class BranchService:
    @staticmethod
    async def get_branch_by_ifsc(db: AsyncSession, ifsc: str) -> Optional[Branch]:
        """Get branch by IFSC code with bank details"""
        result = await db.execute(
            select(Branch, Bank.name.label('bank_name'))
            .join(Bank, Branch.bank_id == Bank.id)
            .where(Branch.ifsc == ifsc.upper())
        )
        row = result.first()
        if row:
            branch = row[0]
            branch.bank_name = row[1]
            return branch
        return None
    
    @staticmethod
    async def search_branches(
        db: AsyncSession,
        query: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        bank_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Branch], int]:
        """Search branches with multiple filters"""
        base_query = select(Branch, Bank.name.label('bank_name')).join(Bank, Branch.bank_id == Bank.id)
        count_query = select(func.count(Branch.ifsc)).join(Bank, Branch.bank_id == Bank.id)
        
        filters = []
        
        if query:
            search_filter = f"%{query}%"
            filters.append(
                or_(
                    Branch.ifsc.ilike(search_filter),
                    Branch.branch.ilike(search_filter),
                    Branch.address.ilike(search_filter),
                    Bank.name.ilike(search_filter)
                )
            )
        
        if city:
            filters.append(Branch.city.ilike(f"%{city}%"))
        
        if state:
            filters.append(Branch.state.ilike(f"%{state}%"))
        
        if district:
            filters.append(Branch.district.ilike(f"%{district}%"))
        
        if bank_id:
            filters.append(Branch.bank_id == bank_id)
        
        if filters:
            base_query = base_query.where(*filters)
            count_query = count_query.where(*filters)
        
        # Get total count
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get branches
        result = await db.execute(base_query.offset(skip).limit(limit))
        
        branches = []
        for row in result.all():
            branch = row[0]
            branch.bank_name = row[1]
            branches.append(branch)
        
        return branches, total
    
    @staticmethod
    async def get_branches_by_bank_id(
        db: AsyncSession, 
        bank_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Branch], int]:
        """Get branches by bank ID with pagination"""
        # Get total count
        count_result = await db.execute(
            select(func.count(Branch.ifsc)).where(Branch.bank_id == bank_id)
        )
        total = count_result.scalar()
        
        # Get branches with bank name
        result = await db.execute(
            select(Branch, Bank.name.label('bank_name'))
            .join(Bank, Branch.bank_id == Bank.id)
            .where(Branch.bank_id == bank_id)
            .offset(skip)
            .limit(limit)
        )
        
        branches = []
        for row in result.all():
            branch = row[0]
            branch.bank_name = row[1]
            branches.append(branch)
        
        return branches, total
    
    @staticmethod
    async def get_branch_count(db: AsyncSession) -> int:
        """Get total number of branches"""
        result = await db.execute(select(func.count(Branch.ifsc)))
        return result.scalar()
    
    @staticmethod
    async def create_branch(db: AsyncSession, branch: BranchCreate) -> Branch:
        """Create a new branch"""
        db_branch = Branch(**branch.dict())
        db.add(db_branch)
        await db.commit()
        await db.refresh(db_branch)
        return db_branch
