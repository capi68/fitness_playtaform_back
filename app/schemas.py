from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

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