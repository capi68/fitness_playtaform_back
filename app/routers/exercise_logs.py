from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/exercise-logs", tags=["Exercise Logs"])

######################
#POST /exercise-logs
######################

@router.post("/")
def create_exercise_log(
    log: schemas.ExerciseLogCreate,
    db: Session = Depends(get_db),
    current_user: models.Trainer = Depends(get_current_user)
):
    session_check = db.query(models.WorkoutSession).join(models.Client).filter(
        models.WorkoutSession.id == log.workout_session_id,
        models.Client.trainer_id == current_user.id
    ).first()

    if not session_check:
        raise HTTPException(status_code=404, detail="Workout Session not found")
    
    existing_sets = db.query(models.ExerciseLog.set_number).filter(
        models.ExerciseLog.workout_session_id == log.workout_session_id,
        models.ExerciseLog.workout_day_exercise_id == log.workout_day_exercise_id
    ).all()

    set_number = max([s[0] for s in existing_sets], default=0) + 1
    
    new_log = models.ExerciseLog(
        workout_session_id=log.workout_session_id,
        workout_day_exercise_id=log.workout_day_exercise_id,
        set_number=set_number,
        reps_done=log.reps_done,
        rpe=log.rpe,
        rir=log.rir
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log