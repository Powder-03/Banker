from pydantic import BaseModel
from typing import Optional

class BranchBase(BaseModel):
    ifsc: str
    branch: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

class BranchCreate(BranchBase):
    bank_id: int

class Branch(BranchBase):
    bank_id: int
    bank_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class BranchDetail(Branch):
    pass
