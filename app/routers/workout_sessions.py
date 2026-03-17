from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(tags=["Workout Sessions"])



######################################
#POST /workout-plans/workout-sessions
######################################

@router.post("/clients/{client_id}/workout-sessions")
def start_workout_session(
    client_id: int,
    session: schemas.WorkoutSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.Trainer = Depends(get_current_user)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    new_session = models.WorkoutSession(
        client_id=client_id,
        workout_day_id=session.workout_day_id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session

#####################################
#GET /workout-sessions/{sessions_id}
#####################################

@router.get("/workout-sessions/{sessions_id}")
def get_workout_session(
    session_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(models.WorkoutSession).options(
        joinedload(models.WorkoutSession.logs)
        .joinedload(models.ExerciseLog.workout_day_exercise)
        .joinedload(models.WorkoutDayExercise.exercise)
    ).join(models.Client).filter(
        models.WorkoutSession.id == session_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Workout Session not found")
    
    return session

#########################################
#GET /clients/{client_id}/current-workout
#########################################

@router.get("/clients/{client_id}/current-workout")
def get_current_workout(
    client_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workout = db.query(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.client_id == client_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    return workout

###############################
#GET /workout-plans/{id}/days
###############################

@router.get("/workout-plans/{plan_id}/days")
def get_workout_days(
    plan_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    days = db.query(models.WorkoutDay).join(models.WorkoutPlan).join(models.Client).filter(
        models.WorkoutPlan.id == plan_id,
        models.Client.trainer_id == current_user.id
    ).all()

    if not days:
        raise HTTPException(status_code=404, detail="Workout days not found")
    
    return days

######################################
#GET /workout-days/{day_id}/exercises
######################################

@router.get("/workout-days/{day_id}/exercises")
def get_workout_exercises(
    day_id: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exercises = (
        db.query(models.WorkoutDayExercise)
        .options(joinedload(models.WorkoutDayExercise.exercise))
        .join(models.WorkoutDay)
        .join(models.WorkoutPlan)
        .join(models.Client)
        .filter(
            models.WorkoutDay.id == day_id,
            models.Client.trainer_id == current_user.id
        ).all()
    )
    
    if not exercises:
        raise HTTPException(status_code=404, detail="Exercises not found")
    
    return exercises

