from fastapi import APIRouter, HTTPException, Depends
from ..database import SessionDep
from .. models.sql_models import AuthorBase,AuthorDB
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from ..auth import is_admin

router = APIRouter(tags=['authors'])

@router.get('/authors/get')
def get_authors(session:SessionDep):
    authors = session.exec(select(AuthorDB)).all()
    return authors


@router.post('/authors/create',status_code=203)
def create_author(author:AuthorBase, session:SessionDep, admin=Depends(is_admin)):
    try:
        author_db = AuthorDB(**author.model_dump())
        session.add(author_db)
        session.commit()
        session.refresh(author_db)
        return author_db
        
    except IntegrityError as e:
        raise HTTPException(status_code=402, detail="This author is already created")