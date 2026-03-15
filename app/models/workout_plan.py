from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..database import Base

###################################################
#Models relations Trainer >> Clients >> WorkoutPlan
###################################################

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("workout_templates.id"), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="workout_plans") 
    days = relationship("WorkoutDay", back_populates="workout_plan", cascade="all, delete")

class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    order = Column(Integer)

    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"))

    workout_plan = relationship("WorkoutPlan", back_populates="days")
    exercises = relationship("WorkoutDayExercise", back_populates="workout_day", cascade="all, delete")

class WorkoutDayExercise(Base):
    __tablename__ = "workout_day_exercises"

    id = Column(Integer, primary_key=True)
    order = Column(Integer)

    target_sets = Column(Integer)
    target_reps = Column(Integer)
    rest_seconds = Column(Integer)
    notes = Column(Text)

    workout_day_id = Column(Integer, ForeignKey("workout_days.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    logs = relationship("ExerciseLog", back_populates="workout_day_exercise", cascade="all, delete")
    workout_day = relationship("WorkoutDay", back_populates="exercises")
    exercise = relationship("Exercise")
