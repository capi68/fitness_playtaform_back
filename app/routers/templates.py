from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..security import get_current_user

router = APIRouter(prefix="/templates", tags=["Templates"])

################
#POST "/"
################

@router.post("/")
def create_template(
    name: str,
    description: str | None = None,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = models.WorkoutTemplate(
        name=name,
        description=description,
        trainer_id=current_user.id
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template

####################################
#POST /templates/{template_id}/days
####################################

@router.post("/{template_id}/days")
def create_template_days(
    template_id: int,
    name: str,
    order: int,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = db.query(models.WorkoutTemplate).filter(
        models.WorkoutTemplate.id == template_id,
        models.WorkoutTemplate.trainer_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="template not found")
    
    day = models.TemplateDay(
        name=name,
        order=order,
        template_id=template_id
    )

    db.add(day)
    db.commit()
    db.refresh(day)

    return day

########################################
#POST /template-days/{day_id}/exercises
########################################

@router.post("/template-days/{day_id}/exercises")
def create_exercises_day(
    day_id: int,
    order: int,
    target_sets: int,
    target_reps: int,
    rest_seconds: int,
    template_day_id: int,
    exercise_id: int,
    notes: str | None = None,
    current_user: models.Trainer = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    day = db.query(models.TemplateDay).join(models.WorkoutTemplate).filter(
        models.TemplateDay.id == day_id,
        models.WorkoutTemplate.trainer_id == current_user.id
    ).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    
    exercise = models.TemplateDayExercise(
        order=order,
        target_sets=target_sets,
        target_reps=target_reps,
        rest_seconds=rest_seconds,
        template_day_id=template_day_id,
        exercise_id=exercise_id,
        notes=notes

    )

    db.add(exercise)
    db.commit()
    db.refresh(exercise)

    return exercise