from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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