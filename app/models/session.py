from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..database import Base

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    workout_day_id = Column(Integer, ForeignKey("workout_days.id"))

    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    trainer_feedback = Column(Text)

    logs = relationship("ExerciseLog", back_populates="session", cascade="all, delete")