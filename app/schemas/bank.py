from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class BankBase(BaseModel):
    name: str

class BankCreate(BankBase):
    id: int

class Bank(BankBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class BankList(BaseModel):
    id: int
    name: str
    branch_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

# Define BankDetail without forward reference for now
class BankDetail(BankBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
