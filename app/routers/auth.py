from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


################################
#POST /auth/login to verify user 
################################

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    #Search User by Email
    trainer = db.query(models.Trainer).filter(models.Trainer.email == form_data.username).first()

    #Don't exist ERROR
    if not trainer:
        raise HTTPException(status_code=401, detail="Email invalido")
    
    #verify PASSWORD
    if not verify_password(form_data.password, trainer.password_hash):
        raise HTTPException(status_code=401, detail="Clave invalida")
    
    access_token = create_access_token( data={"sub": trainer.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }