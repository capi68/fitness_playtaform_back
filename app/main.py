from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, get_db 
from . import models, schemas
from .schemas import TrainersListResponse,  ClientUpdate, ClientResponse
from .security import hash_password, verify_password, get_current_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm


app = FastAPI(title="Fitness Plataform API")

######################
#GET Endpoint Inicial
######################

@app.get("/")
def read_root():
    return {"message": "fitness Plataform API is running"}

##################################
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

#####################################
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

################################
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

##################
#GET PROFILE
##################

@app.get("/profile", response_model=schemas.TrainerResponse)
def read_profile(current_user: str = Depends(get_current_user)):
    return current_user

#################
#POST /clients
#################

@app.post("/clients", response_model=schemas.ClientResponse, status_code=201)
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

#################
#GET /clients
#################

@app.get("/clients", response_model=List[schemas.ClientResponse])
def get_my_clients(
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db),
    
): 
    clients = db.query(models.Client).filter(
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).all()
    return clients

############################
#GET /clients/{client_id}
############################

@app.get("/clients/{client_id}", response_model=schemas.ClientResponse)
def client_by_id(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id, 
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return client

###########################
#PUT /clients/{client_id}
###########################

@app.put("/clients/{client_id}", response_model=schemas.ClientResponse)
def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
    
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for key, value in client_update.model_dump(exclude_unset=True).items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)

    return client

################################
#DELETE /clientes/{client_id}
################################

@app.delete("/clients/{client_id}", status_code=200)
def delete_client(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    client.is_active = False
    db.commit()

    return {"detail": "Cliente desactivado correctamente"}

###################################
#PATCH /clients/{client_id}/restore
###################################

@app.patch("/clients/{client_id}/restore", response_model=schemas.ClientResponse)
def restore_client(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db) 
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == False
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    client.is_active = True
    db.commit()
    db.refresh(client)

    return {"detail": "Cliente activado correctamente"}


#########################
#CRUDS WORKOUTS PLANS
#########################

########################################
#POST /clients/{client_id}/workout-plans
########################################

@app.post("/clients/{client_id}/workout-plans", response_model=schemas.WorkoutPlanResponse, status_code=201)
def create_workout_plan(
    client_id: int,
    workout_plan: schemas.WorkoutPlanCreate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    

    new_workpout_plan = models.WorkoutPlan(
        name=workout_plan.name,
        description=workout_plan.description,
        start_date=workout_plan.start_date,
        end_date=workout_plan.end_date,
        client_id=client_id
    )

    db.add(new_workpout_plan)
    db.commit()
    db.refresh(new_workpout_plan)

    return new_workpout_plan

########################################
#GET /clients/{client_id}/workout-plans
########################################

@app.get("/clients/{client_id}/workout-plans", response_model=List[schemas.WorkoutPlanResponse])
def workout_plan(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    workout_plans = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.client_id == client_id,
        models.WorkoutPlan.is_active == True
    ).all()

    return workout_plans

##################################
#GET /workout-plans/{workout_id}
##################################

@app.get("/workout-plans/{workout_id}", response_model=schemas.WorkoutPlanResponse)
def workout_plan(
    workout_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.id == workout_id,
        models.Client.trainer_id == current_user.id,
        models.WorkoutPlan.is_active == True
    ).first()

    if not workout:
        raise HTTPException(status_code=404, detail="Workout no encontrado")
    
    return workout

######################
#GET /workout-plans
######################

@app.get("/workout-plans", response_model=List[schemas.WorkoutPlanResponse])
def get_all_workout_plans(
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout_plans = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.Client.trainer_id == current_user.id,
        models.WorkoutPlan.is_active == True
    ).all()

    return workout_plans

################################
#PUT /workout-plans/{workout_id}
################################

@app.put("/workout-plans/{workout_id}", response_model=List[schemas.WorkoutPlanResponse])
def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutPlanUpdate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout_plan = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.id == workout_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True,
        models.WorkoutPlan.is_active == True
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan no encontrado")
    
    for key, value in workout_update.model_dump(exclude_unset=True).items():
        setattr(workout_plan, key, value)

    db.commit()
    db.refresh(workout_plan)
    
    return workout_plan

###################################
#DELETE /workout-plans/{workout_id} (soft delete)
###################################

@app.delete("/workout-plans/{workout_id}", response_model=schemas.WorkoutPlanResponse)
def delete_workout(
    workout_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.id == workout_id,
        models.Client.trainer_id == current_user.id,
        models.WorkoutPlan.is_active == True
    ).first()

    if not workout:
        raise HTTPException(status_code=404, detail="workout plan no encontrado")
    
    workout.is_active = False
    db.commit()

    return {"detail": "Workout plan desactivado correctamente"}

##########################################
#PATCH /workout-plans/{workout_id}/restore
##########################################

@app.patch("/workout-plans/{workout_id}/restore", status_code=200)
def restore_workout_plan(
    workout_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.id == workout_id,
        models.Client.trainer_id == current_user.id,
        models.Client.is_active == True,
        models.WorkoutPlan.is_active == False
    ).first()

    if not workout:
        raise HTTPException(status_code=404, detail="Workout no encontrado")
    
    workout.is_active = True
    db.commit()

    return {"detail": "Workout reactivado correctamente"}

