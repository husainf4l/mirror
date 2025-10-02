from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
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
    
    # Relationships
    relation_type = relationship("RelationType", back_populates="guests")
    video_recordings = relationship("VideoRecording", back_populates="guest")
    
    def __repr__(self):
        return f"<Guest(id={self.id}, name='{self.first_name} {self.last_name}', relation='{self.relation}')>"
    
    @property 
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class VideoRecording(Base):
    __tablename__ = "video_recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(100), nullable=False, index=True)  # LiveKit room ID
    video_url = Column(Text, nullable=False)  # Direct S3 URL
    presigned_url = Column(Text, nullable=True)  # Presigned URL (expires)
    egress_id = Column(String(100), nullable=True, index=True)  # LiveKit egress ID
    
    # Guest information
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=True, index=True)
    guest_name = Column(String(200), nullable=True, index=True)  # Stored name for backup
    guest_phone = Column(String(20), nullable=True)
    guest_relation = Column(String(100), nullable=True)
    guest_table = Column(String(10), nullable=True)
    
    # Recording metadata
    recording_started_at = Column(DateTime, nullable=True)
    recording_ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Status and processing
    is_processed = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)  # For soft delete
    processing_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    guest = relationship("Guest", back_populates="video_recordings")
    
    def __repr__(self):
        return f"<VideoRecording(id={self.id}, room_id='{self.room_id}', guest='{self.guest_name}', status='{self.processing_status}')>"
    
    @property
    def s3_key(self):
        """Extract S3 key from video URL"""
        if "amazonaws.com/" in self.video_url:
            return self.video_url.split("amazonaws.com/")[-1]
        return None
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "video_url": self.video_url,
            "presigned_url": self.presigned_url,
            "egress_id": self.egress_id,
            "guest_id": self.guest_id,
            "guest_name": self.guest_name,
            "guest_phone": self.guest_phone,
            "guest_relation": self.guest_relation,
            "guest_table": self.guest_table,
            "recording_started_at": self.recording_started_at.isoformat() if self.recording_started_at else None,
            "recording_ended_at": self.recording_ended_at.isoformat() if self.recording_ended_at else None,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "is_processed": self.is_processed,
            "is_available": self.is_available,
            "processing_status": self.processing_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "s3_key": self.s3_key
        }