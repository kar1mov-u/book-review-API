from fastapi import APIRouter, HTTPException,Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from ..database import SessionDep
from ..models.sql_models import UserDB,UserBase, Activity,ActivityReturn
from ..utils import hashing_pass,verify_pass
from ..auth import craete_access_token,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
router = APIRouter(tags=['user'])

@router.get('/users')
def get_users(session:SessionDep):
    users = session.exec(select(UserDB)).all()
    return users

@router.post('/users/create')
def create_user(user:UserBase, session:SessionDep):
    user.password = hashing_pass(user.password)
    user_db = UserDB(**user.model_dump())
    try:
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email or Username is already registered")
    

@router.post('/login')
def login(session:SessionDep, user_data:OAuth2PasswordRequestForm=Depends()):
    user_db = session.exec(select(UserDB).where(UserDB.email==user_data.username)).first()
    if not user_db:
        raise HTTPException(status_code=403,detail="Invalid credentials")
    if not verify_pass(user_data.password,user_db.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=30)
    access_token= craete_access_token(data={"sub":user_db.email}, expires_delta=access_token_expires)
    
    return access_token
    

@router.get('/users/me')
def get_my_user(user:UserDB=Depends(get_current_user)):
    return user

@router.get('/users/activity')
def get_activity(session:SessionDep, user=Depends(get_current_user)):
    acts = session.exec(select(Activity).where(Activity.user_id==user.id)).all()
    comms,reviews = [],[]
    for act in acts:
        a=ActivityReturn(id=act.id, book_name=act.book_id, detail=act.detail)
        
        if act.activity_type=="comment":
            comms.append(a)
        else:
            reviews.append(a)
    return {"comments":comms, "reviews":reviews}
            
        

