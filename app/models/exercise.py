from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    video_url = Column(String)
    muscle_group = Column(String)
    is_active = Column(Boolean, default=True, nullable=False )

    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trainer = relationship("Trainer", back_populates="exercises")