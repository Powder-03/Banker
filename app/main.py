from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import get_db
from app.services.bank_service import BankService
from app.services.branch_service import BranchService

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="REST API for Indian Banks and Branches data",
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    return {
        "message": "Indian Bank API", 
        "version": settings.version,
        "docs": "/docs",
        "description": "REST API for Indian Banks and Branches"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "sqlite"}

@app.get("/stats")
async def get_database_stats(db: AsyncSession = Depends(get_db)):
    """Get comprehensive database statistics"""
    try:
        # Get bank count
        bank_count = await BankService.get_bank_count(db)
        
        # Get branch count
        branch_count = await BranchService.get_branch_count(db)
        
        # Get sample branches to check states
        sample_branches, _ = await BranchService.search_branches(
            db, limit=1000, skip=0
        )
        unique_states = len(set(branch.state for branch in sample_branches if branch.state))
        unique_cities = len(set(branch.city for branch in sample_branches if branch.city))
        
        return {
            "banks_total": bank_count,
            "branches_total": branch_count,
            "unique_states": unique_states,
            "unique_cities": unique_cities,
            "database_type": "SQLite",
            "status": "operational"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
