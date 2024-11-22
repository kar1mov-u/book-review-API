from fastapi import APIRouter, HTTPException,Depends
from sqlmodel import select
from typing import List
# from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from ..database import SessionDep
from ..models.sql_models import BookDB,BookCreate,GenreDB,BookReturn,GenreBase,ReviewBase, ReviewDB,ReviewReturn
from ..auth import get_current_user

router = APIRouter()

@router.get('/books')
def get_books(session:SessionDep):
    books = session.exec(select(BookDB).options(joinedload(BookDB.genres))).unique().all()

    # return_objects = []
    # for book in books:
    #         b= BookReturn(id=book.id,
    #                       title=book.title,
    #                       author=book.author,
    #                       published=book.published,
    #                       genres=[GenreBase(name=genre.name, id=genre.id) for genre in book.genres] )
    #         return_objects.append(b)
    return books



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


        
@router.get('/books/{id}')
def get_book(id:int,session:SessionDep):
    book = session.exec(
        select(BookDB)
        .options(
            joinedload(BookDB.genres),
            joinedload(BookDB.reviews)
            )
        .where(BookDB.id ==id)
        ).unique().first()
    if not book:
        raise HTTPException(status_code=404, detail="There is no such book")
    return BookReturn(
        id=book.id,
        title=book.title,
        author=book.author,
        published=book.published,
        genres=[GenreBase(id=genre.id, name=genre.name) for genre in book.genres],
        reviews=[ReviewReturn(message=review.message,id=review.id, user_id=review.user_id,created_at=review.created_at) for review in book.reviews])


@router.post('/books/comment/{id}')
def commen_book(id:int, comment:ReviewBase, session: SessionDep,user=Depends(get_current_user)):
    data = comment.model_dump()
    book = session.get(BookDB,id)
    if not book:
        raise HTTPException(status_code=402,detail="There is no such book")
    comment_db = ReviewDB(**data, book_id=id,user_id=user.id)
    session.add(comment_db)
    session.commit()
    return {"msg":"Success"}
    