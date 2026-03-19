from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/exercises", tags=["Exercises"])

#################
#GET /exercises
#################

@router.get("/", response_model=List[schemas.ExerciseResponse])
def get_my_exercises(
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    my_exercises = db.query(models.Exercise).filter(
        models.Exercise.trainer_id == current_user.id,
        models.Exercise.is_active == True
    ).all()

    return my_exercises

#####################
#GET /exercises/{id}
#####################

@router.get("/{id}", response_model=schemas.ExerciseResponse)
def get_exercise(
    id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exercise = db.query(models.Exercise).filter(
        models.Exercise.id == id,
        models.Exercise.trainer_id == current_user.id,
        models.Exercise.is_active == True
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise



#################
#POST /exercises
#################

@router.post("/", response_model=schemas.ExerciseResponse, status_code=201)
def new_exercise(
    exercise: schemas.ExerciseCreate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clean_name = exercise.name.strip()

    existing = db.query(models.Exercise).filter(
        models.Exercise.trainer_id == current_user.id,
        func.lower(models.Exercise.name) == clean_name.lower(),
        models.Exercise.is_active == True
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Exercise already exists")

    exercise = models.Exercise(
        **exercise.model_dump(),
        name=clean_name,
        trainer_id=current_user.id
    )

    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    return exercise

################
#PUT /exercises
################

@router.put("/{id}", response_model=schemas.ExerciseResponse)
def update_exercise(
    id: int,
    exercise_update: schemas.ExerciseUpdate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exercise = db.query(models.Exercise).filter(
        models.Exercise.id == id,
        models.Exercise.trainer_id == current_user.id,
        models.Exercise.is_active == True
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exersise not found")
    
    for key, value in exercise_update.model_dump(exclude_unset=True).items():
        setattr(exercise, key, value)
    
    db.commit()
    db.refresh(exercise)

    return exercise

#######################
#DELETE /exercise/{id}
#######################

@router.delete("/{id}")
def inactive_exercise(
    id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exercise = db.query(models.Exercise).filter(
        models.Exercise.id == id,
        models.Exercise.trainer_id == current_user.id,
        models.Exercise.is_active == True
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    exercise.is_active = False

    db.commit()
    db.refresh(exercise)

    return {"detail": "Exercise inactive correctly"}

