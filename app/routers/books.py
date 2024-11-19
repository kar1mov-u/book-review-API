from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from ..database import SessionDep
from ..models.sql_models import BookDB,BookCreate,GenreDB

router = APIRouter()

@router.get('/books')
def get_books(session:SessionDep):
    books = session.exec(select(BookDB)).all()
    return books

@router.post('/books/add')
async def create_book(book_data:BookCreate, session: SessionDep):
    book=book_data.book
    genres = book_data.genres
    print(book)
    print(genres)
    
    genre_objects = []
    for genre_name in genres:
        genre = session.exec(select(GenreDB).where(GenreDB.name==genre_name)).scalars().first()
        if not genre:
            genre = GenreDB(name=genre_name)
            session.add(genre)
        genre_objects.append(genre)
    
    try:
        new_book = BookDB(**book.model_dump(),genres=genre_objects)
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
    except IntegrityError:
        raise HTTPException(detail="The book is already in use")
    return new_book
        
        
    


