import jwt
from jwt.exceptions import InvalidTokenError
from datetime import timedelta,datetime,timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException
from .models.sql_models import UserDB
from pydantic import BaseModel
from .database import SessionDep
from sqlmodel import select

class TokenType(BaseModel):
    token_type: str
    access_token: str


ouath2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


SECRET_KEY='31bb6132fe4890d1740653c2bc25bfe6895bc355a1b9613a0609c8822519d6ab'
ALGHORITH="HS256"
ACCESS_TOKEN_EXPIRE_MINUTE= 30

def craete_access_token(data:dict, expires_delta:timedelta| None=None):
    to_decode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=15)
    to_decode.update({"exp":expire})
    encoded_jwt= jwt.encode(to_decode, SECRET_KEY, algorithm=ALGHORITH)
    return TokenType(token_type="Bearer", access_token=encoded_jwt)    
 
def get_current_user(session:SessionDep, token:str=Depends(ouath2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGHORITH])
        user_email = payload.get('sub')
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid Credentials")
    except InvalidTokenError:
        raise credentials_exception
    
    user = session.exec(select(UserDB).where(UserDB.email==user_email)).first()
    if not user:
        raise credentials_exception
    return user
    
    