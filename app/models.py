from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from .database import Base



#######################################
#Models relations Trainers>>Clients
#######################################

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscription_plan = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clients = relationship("Client", back_populates="trainer")
    exercises = relationship("Exercise", back_populates="trainer")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    goal = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trainer_id = Column(Integer, ForeignKey("trainers.id"))

    trainer = relationship("Trainer", back_populates="clients")
    workout_plans = relationship("WorkoutPlan", back_populates="client")

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

##################
#Rutine models
##################

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    video_url = Column(String)
    muscle_group = Column(String)

    trainer_id = Column(Integer, ForeignKey("trainers.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trainer = relationship("Trainer", back_populates="exercises")

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

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey("clients.id"))
    workout_day_id = Column(Integer, ForeignKey("workout_days.id"))

    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    trainer_feedback = Column(Text)

    logs = relationship("ExerciseLog", back_populates="session", cascade="all, delete")

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
