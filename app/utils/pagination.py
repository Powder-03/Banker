from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool = False
    has_prev: bool = False
    
    def __init__(self, **data):
        super().__init__(**data)
        self.has_next = self.skip + self.limit < self.total
        self.has_prev = self.skip > 0
