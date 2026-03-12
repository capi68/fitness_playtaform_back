from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/workout-plans", tags=["Workout Plans"])


##################################
#GET /workout-plans/{workout_id}
##################################

@router.get("/{workout_id}", response_model=schemas.WorkoutPlanResponse)
def workout_plan(
    workout_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutPlan).options(
        selectinload(models.WorkoutPlan.days)
        .selectinload(models.WorkoutDay.exercises)
    ).join(models.Client).filter(
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

@router.get("/", response_model=List[schemas.WorkoutPlanResponse])
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

@router.put("/{workout_id}", response_model=schemas.WorkoutPlanResponse)
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

@router.delete("/{workout_id}", response_model=schemas.WorkoutPlanResponse)
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
        raise HTTPException(status_code=404, detail="workout plan not found")
    
    workout.is_active = False
    db.commit()
    db.refresh(workout)

    return workout

##########################################
#PATCH /workout-plans/{workout_id}/restore
##########################################

@router.patch("/{workout_id}/restore", status_code=200)
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





