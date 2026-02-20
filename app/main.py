from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, get_db 
from . import models, schemas
from .schemas import TrainersListResponse
from .security import hash_password, verify_password


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness Plataform API")


#GET Endpoint Inicial
###################

@app.get("/")
def read_root():
    return {"message": "fitness Plataform API is running"}

#POST  Endpoint To Upload Trainers
##################################

@app.post("/trainers", response_model=schemas.TrainerResponse)
def create_trainer(trainer: schemas.TrainerCreate, db: Session = Depends(get_db)):
    
    db_trainer = models.Trainer(
        name=trainer.name,
        email=trainer.email,
        password_hash=hash_password(trainer.password)
    )

    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)

    return db_trainer

#GET Endpoint to obtain Trainers list
#####################################

@app.get("/trainers", response_model=TrainersListResponse)
def get_trainers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(models.Trainer).count()

    Trainers = (
        db.query(models.Trainer)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": Trainers
    }

#POST /auth/login to verify user 
################################

@app.post("/auth/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    #Search User by Email
    trainer = db.query(models.Trainer).filter(models.Trainer.email == data.email).first()

    #Don't exist ERROR
    if not trainer:
        raise HTTPException(status_code=401, detail="Email invalido")
    
    #verify PASSWORD
    if not verify_password(data.password, trainer.password_hash):
        raise HTTPException(status_code=401, detail="Clave invalida")
    
    #OK
    return {"message": "Inicio de sesión exitosa"}