from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
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
    db: Session = Depends(get_db)
    
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
    

    new_workout_plan = models.WorkoutPlan(
        name=workout_plan.name,
        description=workout_plan.description,
        start_date=workout_plan.start_date,
        end_date=workout_plan.end_date,
        client_id=client_id
    )

    db.add(new_workout_plan)
    db.commit()
    db.refresh(new_workout_plan)

    return new_workout_plan

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

########################################################
#POST /clients/{client_id}/assign-template/{template_id}
########################################################

@router.post("/{client_id}/assign-template/{template_id}")
def assign_template_client(
    client_id: int,
    template_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    template = db.query(models.WorkoutTemplate).filter(
        models.WorkoutTemplate.trainer_id == current_user.id,
        models.WorkoutTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="template not found")
    
    workout = models.WorkoutPlan(
        client_id=client.id,
        template_id=template.id
    )

    db.add(workout)
    db.flush()

    for day in template.days:
        new_day = models.WorkoutDay(
            workout_plan_id=workout.id,
            name=day.name,
            order=day.order
        )

        db.add(new_day)
        db.flush()
    
        for exercise in day.exercises:

            new_exercise = models.WorkoutDayExercise(
                workout_day_id=new_day.id,
                exercise_id=exercise.exercise_id,
                order=exercise.order,
                target_sets=exercise.target_sets,
                target_reps=exercise.target_reps,
                rest_seconds=exercise.rest_seconds,
                notes=exercise.notes
            )

            db.add(new_exercise)
    
    db.commit()
    db.refresh(workout)

    return workout

#######################################
#GET /clients/{client_id}/workout-plan
#######################################

@router.get("/{client_id}/workout-plan")
def get_client_workout_plan(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout_plan = db.query(models.WorkoutPlan).options(
        selectinload(models.WorkoutPlan.days)
        .selectinload(models.WorkoutDay.exercises)
    ).join(models.Client).filter(
        models.WorkoutPlan.client_id == client_id,
        models.Client.trainer_id == current_user.id,
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="workout plan not found")
    
    return workout_plan
    
