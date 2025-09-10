from fastapi import APIRouter
from app.api.v1.endpoints import banks, branches

api_router = APIRouter()
api_router.include_router(banks.router, prefix="/banks", tags=["banks"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
