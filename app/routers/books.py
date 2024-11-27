from fastapi import APIRouter, HTTPException,Depends
from sqlmodel import select,asc
from typing import Optional
# from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from ..database import SessionDep
from ..models.sql_models import BookDB,BookCreate,GenreDB,BookReturn,GenreBase,ReviewBase, ReviewDB,ReviewReturn, PaginatedComments
from ..auth import get_current_user,is_admin

router = APIRouter()

@router.get('/books')
def get_books(session:SessionDep):
    books = session.exec(select(BookDB)).all()

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
async def create_book(book_data:BookCreate, session: SessionDep, admin=Depends(is_admin)):

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
        session.rollback()
        raise HTTPException(status_code=401,detail="The book is already in use")
    return new_book


        
@router.get('/books/{id}')
def get_book(id:int,session:SessionDep):
    book = session.exec(
        select(BookDB) 
        .options(
            joinedload(BookDB.genres)
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
)


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
    
@router.get('/books/{id}/comments')
def get_comments(id:int,session:SessionDep, cursor:Optional[int]=None, limit:int=10 ):
    query = select(ReviewDB).where(ReviewDB.book_id==id)
    if cursor:
        query = query.where(ReviewDB.id>cursor)
    
    query = query.order_by(ReviewDB.id.asc()).limit(limit)
    
    comments = session.exec(query).all()    
    
    if comments:
        next_cursor = comments[-1].id
    else:
        next_cursor= None
    
    response = PaginatedComments(
        comments=  [ReviewReturn(message=comment.message, id=comment.id, user_id= comment.user_id, created_at=comment.created_at ) for comment in comments],
        next_cursor=next_cursor
    )
    
    return response