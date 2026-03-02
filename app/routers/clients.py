from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/clients", tags=["Clients"])

#################
#POST /clients
#################

@router.post("/", response_model=schemas.ClientResponse, status_code=201)
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

@router.get("/", response_model=List[schemas.ClientResponse])
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

@router.get("/{client_id}", response_model=schemas.ClientResponse)
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

@router.put("/{client_id}", response_model=schemas.ClientResponse)
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

@router.delete("/{client_id}", status_code=200)
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

@router.patch("/{client_id}/restore", response_model=schemas.ClientResponse)
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

    return client

########################################
#POST /clients/{client_id}/workout-plans
########################################

@router.post("/{client_id}/workout-plans", response_model=schemas.WorkoutPlanResponse, status_code=201)
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

@router.get("/{client_id}/workout-plans", response_model=List[schemas.WorkoutPlanResponse])
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
