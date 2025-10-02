from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class RelationType(Base):
    __tablename__ = "relation_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "Bride's Family", "Groom's Family", "Friend", etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    guests = relationship("Guest", back_populates="relation_type")

class Guest(Base):
    __tablename__ = "guests"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True, unique=True)
    seat_number = Column(String(10), nullable=True)
    relation = Column(String(100), nullable=True)  # Free text relation
    relation_type_id = Column(Integer, ForeignKey("relation_types.id"), nullable=True)
    message = Column(Text, nullable=True)  # Personal message from/to the guest
    story = Column(Text, nullable=True)   # Story or memory about the guest
    about = Column(Text, nullable=True)   # Additional information about the guest
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    relation_type = relationship("RelationType", back_populates="guests")
    
    def __repr__(self):
        return f"<Guest(id={self.id}, name='{self.first_name} {self.last_name}', relation='{self.relation}')>"
    
    @property 
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()