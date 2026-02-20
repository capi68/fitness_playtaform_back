import os 
from passlib.context import CryptContext
from jose import JWTError, jwt 
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer


load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#JWT 
##########

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")

#PASSWORD HASHING 
#################

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#CREATE TOKEN
#############

def create_access_token(data: dict):
    to_encode = data.copy()

    #Expiration claim
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    #Encode token with secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#DECODE TOKEN
#############

def deconde_access_token(token: str):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = deconde_access_token(token)
    user_email = payload.get("sub")

    if user_email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )
    
    return user_email