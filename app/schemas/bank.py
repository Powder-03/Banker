from pydantic import BaseModel
from typing import List, Optional

class BankBase(BaseModel):
    name: str

class BankCreate(BankBase):
    id: int

class Bank(BankBase):
    id: int
    
    class Config:
        from_attributes = True

class BankList(BaseModel):
    id: int
    name: str
    branch_count: Optional[int] = 0
    
    class Config:
        from_attributes = True
