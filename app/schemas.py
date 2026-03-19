from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from enum import Enum

###################################
#Schemas create Trainer and Clients
###################################

class TrainerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class TrainerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    subscription_plan: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TrainersListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[TrainerResponse]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str

class ClientCreate(BaseModel):
    name: str
    age: int
    goal: str

class ClientResponse(BaseModel):
    id: int
    name: str
    age: int
    goal: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    goal: Optional[str] = None

######################
#Schemas WorkoutPlans
######################

class WorkoutPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class WorkoutPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    client_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutSessionCreate(BaseModel):
    workout_day_id: int

class ExerciseLogCreate(BaseModel):
    workout_session_id: int
    workout_day_exercise_id: int
    set_number: int
    reps_done: int
    weight_used: float
    rpe: Optional[float] = None
    rir: Optional[float] = None

##########################################
#Schemas create workout days and exercise
##########################################

class workoutDayCreate(BaseModel):
    name: str
    order: int

class ExerciseShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class WorkoutDayExerciseResponse(BaseModel):
    id: int
    order: int
    exercise: ExerciseShort
    target_sets: int
    target_reps: int
    rest_seconds: int
    notes: str | None = None

    class config:
        from_attibutes = True

class WorkoutDayResponse(BaseModel):
    id: int
    name: str
    order: int
    exercises: list[WorkoutDayExerciseResponse]

    class Config:
        from_attributes = True


class WorkoutDayExerciseCreate(BaseModel):
    exercise_id: int
    order: int | None = None
    target_sets: int | None = None
    target_reps: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None

#############################
#Schemas to create Exercises
#############################

class MuscleGroup(str, Enum):
    chest = "chest"
    back = "back"
    quads = "quads"
    hamstrings = "hamstrings"
    glutes = "glutes"
    calves = "calves"
    shoulders = "shoulders"
    biceps = "biceps"
    triceps = "triceps"
    core = "core"

class ExerciseCreate(BaseModel):
    name: str
    description: str | None = None
    video_url: str | None = None
    muscle_group: MuscleGroup

class ExerciseResponse(BaseModel):
    id: int
    name: str
    description: str | None
    video_url: str | None
    muscle_group: MuscleGroup
    is_active: bool

    class config:
        from_attributes = True

class ExerciseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    video_url: str | None = None
    muscle_group: MuscleGroup | None = None

