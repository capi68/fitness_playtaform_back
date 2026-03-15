from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..database import Base

class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trainer = relationship("Trainer")
    days = relationship("TemplateDay", back_populates="template", cascade="all, delete")

class TemplateDay(Base):
    __tablename__ = "template_days"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    order = Column(Integer)

    template_id = Column(Integer, ForeignKey("workout_templates.id"))

    template = relationship("WorkoutTemplate", back_populates="days")
    exercises = relationship("TemplateDayExercise", back_populates="template_day", cascade="all, delete")

class TemplateDayExercise(Base): 
    __tablename__ = "template_day_exercises"

    id = Column(Integer, primary_key=True)
    order = Column(Integer)

    target_sets = Column(Integer)
    target_reps = Column(Integer)
    rest_seconds = Column(Integer)
    notes = Column(Text)

    template_day_id = Column(Integer, ForeignKey("template_days.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    template_day = relationship("TemplateDay", back_populates="exercises")
    exercise = relationship("Exercise")

