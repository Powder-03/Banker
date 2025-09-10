from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Bank(Base):
    __tablename__ = "banks"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(49), nullable=False)
    
    # Relationship
    branches = relationship("Branch", back_populates="bank")
