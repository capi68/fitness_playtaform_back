from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/workout-days", tags=["Workout Days Exercises"])

######################################
#GET /workout-days/{day_id}/exercises
######################################

@router.get("/{day_id}/exercises", response_model=schemas.WorkoutDayResponse)
def get_day_exercises(
    day_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    day = (
        db.query(models.WorkoutDay)
        .join(models.WorkoutPlan)
        .join(models.Client)
        .filter(
            models.WorkoutDay.id == day_id,
            models.Client.trainer_id == current_user.id
        )
        .options(
            joinedload(models.WorkoutDay.exercises)
            .joinedload(models.WorkoutDayExercise.exercise)
        )
        .first()
    )

    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    
    return day

#######################################
#POST /workout-days/{day_id}/exercises
#######################################

@router.post("/{day_id}/exercises", status_code=201)
def add_exercise_to_day(
    day_id: int,
    exercise: schemas.WorkoutDayExerciseCreate,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    day = db.query(models.WorkoutDay).join(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutDay.id == day_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not day:
        raise HTTPException(status_code=404, detail="Workout day not found")
    
    exercise_db = db.query(models.Exercise).filter(
        models.Exercise.id == exercise.exercise_id,
        models.Exercise.trainer_id == current_user.id,
        models.Exercise.is_active == True
    ).first()

    if not exercise_db:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    if exercise.order is None:
        last_order = db.query(
            func.max(models.WorkoutDayExercise.order)
        ).filter(
            models.WorkoutDayExercise.workout_day_id == day_id
        ).scalar()

        order = 1 if last_order is None else last_order + 1
    else: 
        order = exercise.order

    new_exercise = models.WorkoutDayExercise(
        workout_day_id=day_id,
        exercise_id=exercise_db.id,
        order=order,
        target_sets=exercise.target_sets,
        target_reps=exercise.target_reps,
        rest_seconds=exercise.rest_seconds,
        notes=exercise.notes
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise
