from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..schemas import TrainersListResponse
from ..database import get_db
from .. import models, schemas
from ..security import get_current_user, hash_password

router = APIRouter(prefix="/trainers", tags=["Trainers"])



##################################
#POST  Endpoint To Upload Trainers
##################################

@router.post("/", response_model=schemas.TrainerResponse)
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

@router.get("/", response_model=TrainersListResponse)
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



##################
#GET PROFILE
##################

@router.get("/profile", response_model=schemas.TrainerResponse)
def read_profile(current_user: str = Depends(get_current_user)):
    return current_user

