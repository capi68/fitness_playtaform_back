from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, get_db 
from . import models, schemas
from .schemas import TrainersListResponse
from .security import hash_password, verify_password, get_current_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm


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

@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    #Search User by Email
    trainer = db.query(models.Trainer).filter(models.Trainer.email == form_data.username).first()

    #Don't exist ERROR
    if not trainer:
        raise HTTPException(status_code=401, detail="Email invalido")
    
    #verify PASSWORD
    if not verify_password(form_data.password, trainer.password_hash):
        raise HTTPException(status_code=401, detail="Clave invalida")
    
    access_token = create_access_token( data={"sub": trainer.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

#GET PROFILE
############

@app.get("/profile")
def read_profile(current_user: str = Depends(get_current_user)):
    return{"message": f"Bienvenido {current_user.name}"}

#POST /clients

@app.post("/clients")
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.Trainer = Depends(get_current_user)
):
    new_client = models.Client(
        name=client.name,
        age=client.age,
        goal=client.goal,
        trainer_id=current_user.id
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client

#GET /clients
#################

@app.get("/clients")
def get_my_clients(
    current_user: models.Trainer = Depends(get_current_user)
): 
    return current_user.clients