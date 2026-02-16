from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, get_db 
from . import models, schemas


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
        password_hash=trainer.password
    )

    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)

    return db_trainer

#GET Endpoint to obtain Trainers list
#####################################

