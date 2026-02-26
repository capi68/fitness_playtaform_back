from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime

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

class ClientUpdate(BaseModel):
    name: str
    age: int
    goal: str