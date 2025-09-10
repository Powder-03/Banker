from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Branch(Base):
    __tablename__ = "branches"
    
    ifsc = Column(String(11), primary_key=True, index=True)
    bank_id = Column(BigInteger, ForeignKey("banks.id"), nullable=False)
    branch = Column(String(74))
    address = Column(String(195))
    city = Column(String(50))
    district = Column(String(50))
    state = Column(String(26))
    
    # Relationship
    bank = relationship("Bank", back_populates="branches")
