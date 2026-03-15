from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..database import Base


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True)

    workout_session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    workout_day_exercise_id = Column(Integer, ForeignKey("workout_day_exercises.id"))

    set_number = Column(Integer)
    reps_done = Column(Integer)
    weight_used = Column(Float)

    rpe = Column(Float)
    rir = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("WorkoutSession", back_populates="logs")
    workout_day_exercise = relationship("WorkoutDayExercise", back_populates="logs")
