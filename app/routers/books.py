from fastapi import APIRouter, HTTPException
from sqlmodel import select
from typing import List
# from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from ..database import SessionDep
from ..models.sql_models import BookDB,BookCreate,GenreDB,BookReturn,GenreBase

router = APIRouter()

@router.get('/books',response_model=list[BookReturn])
def get_books(session:SessionDep):
    books = session.exec(select(BookDB).options(joinedload(BookDB.genres))).unique().all()

    return_objects = []
    for book in books:
            b= BookReturn(id=book.id,
                          title=book.title,
                          author=book.author,
                          published=book.published,
                          genres=[GenreBase(name=genre.name, id=genre.id) for genre in book.genres] )
            return_objects.append(b)
    return return_objects

@router.post('/books/add')
async def create_book(book_data:BookCreate, session: SessionDep):
    book=book_data.book
    genres = book_data.genres
    print(book)
    print(genres)
    
    genre_objects = []
    for genre_name in genres:
        genre = session.exec(select(GenreDB).where(GenreDB.name==genre_name)).first()
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
        raise HTTPException(status_code=401,detail="The book is already in use")
    return new_book


        
        
    


