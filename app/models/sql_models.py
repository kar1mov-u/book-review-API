from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from pydantic import BaseModel
from sqlalchemy import ForeignKey

class UserBase(SQLModel):
    username: str=Field(nullable=False,unique=True)
    email: str=Field(nullable=False,unique=True)
    password: str = Field(nullable=False)
    
class UserDB(UserBase, table=True):
    id: int| None=Field(default=None,primary_key=True)
    
    
class UserLogin(SQLModel):
    email: str
    password: str
    
    # __table_args__ = (
    #     {"sqlite_autoincrement":True},
    #     {"unique_constraints":("username", "email")}
    # )
    
    
class BookBase(SQLModel):
    title: str
    author: str
    published: int

class BookGenreLink(SQLModel, table=True):
    book_id: Optional[int]=Field(foreign_key="bookdb.id",primary_key=True)
    genre_id: Optional[int]=Field(foreign_key="genredb.id",primary_key=True)
    
    
class BookDB(BookBase,table=True):
    id: int | None=Field(default=None, primary_key=True)
    rating: float=Field(default=0.0)
    reviews: list['ReviewDB']= Relationship(back_populates="book")
    genres: List["GenreDB"] = Relationship(back_populates="books", link_model=BookGenreLink)


class GenreBase(SQLModel):
    name: str
    id:int
    class Config:
        from_attributes=True
    
class BookReturn(SQLModel):
    id: int
    title: str
    author: str
    published: int
    genres: list[GenreBase]
    
    class Config:
        from_attributes = True
    
    
class GenreDB(SQLModel,table=True):
    id:int | None=Field(default=None, primary_key=True)
    name: str = Field( unique=True)
    books: List[BookDB]=Relationship(back_populates="genres",link_model=BookGenreLink)    


class BookCreate(SQLModel):
    book:BookBase
    genres:List[str]
    
class ReviewBase(SQLModel):
    user_id : int
    positive: bool
    book_id: int=Field(foreign_key="bookdb.id")
    message: str
    
class ReviewDB(ReviewBase,table=True):
    id: int| None = Field(default=None, primary_key=True)
    book:Optional[BookDB]=Relationship(back_populates="reviews")


