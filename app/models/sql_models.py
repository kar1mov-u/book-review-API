from sqlmodel import SQLModel,Field,Relationship
from typing import Optional,List
from datetime import datetime

class UserBase(SQLModel):
    username: str=Field(nullable=False,unique=True)
    email: str=Field(nullable=False,unique=True)
    password: str = Field(nullable=False)
    
class UserDB(UserBase, table=True):
    id: int| None=Field(default=None,primary_key=True)
    is_admin: bool =Field(default=False)
    
class UserLogin(SQLModel):
    email: str
    password: str
    
    # __table_args__ = (
    #     {"sqlite_autoincrement":True},
    #     {"unique_constraints":("username", "email")}
    # )
    
        
class AuthorBase(SQLModel):
    name: str = Field(unique=True, nullable=False)
    birth: int 
    country: str
    
class AuthorDB(AuthorBase, table=True):
    id : int | None = Field(default=None, primary_key=True)
    books: List["BookDB"]= Relationship(back_populates='author')
    
class BookBase(SQLModel):
    title: str = Field(unique=True)
    published: int
    description: str

class BookGenreLink(SQLModel, table=True):
    book_id: Optional[int]=Field(foreign_key="bookdb.id",primary_key=True)
    genre_id: Optional[int]=Field(foreign_key="genredb.id",primary_key=True)
    
    
class BookDB(BookBase,table=True):
    id: int | None=Field(default=None, primary_key=True)
    rating: float=Field(default=0.0)
    rated:int=Field(default=0)
    author_id: int = Field(foreign_key='authordb.id')
    author: Optional[AuthorDB] = Relationship(back_populates="books")
    reviews: List['ReviewDB']= Relationship(back_populates="book")
    genres: List["GenreDB"] = Relationship(back_populates="books", link_model=BookGenreLink)


class GenreBase(SQLModel):
    name: str
    id:int
    class Config:
        from_attributes=True
    

    
    
class GenreDB(SQLModel,table=True):
    id:int | None=Field(default=None, primary_key=True)
    name: str = Field( unique=True)
    books: List[BookDB]=Relationship(back_populates="genres",link_model=BookGenreLink)    


class BookCreate(SQLModel):
    book:BookBase
    author: str
    genres:List[str]
    
class ReviewBase(SQLModel):
    message: str
    
class ReviewDB(ReviewBase,table=True):
    id: int| None = Field(default=None, primary_key=True)
    user_id : int
    created_at:datetime = Field(default_factory=datetime.utcnow)
    book_id: int=Field(foreign_key="bookdb.id")
    
    book:Optional[BookDB]=Relationship(back_populates="reviews")

class ReviewReturn(ReviewBase):
    id : int
    user_id:int
    created_at:datetime

class PaginatedComments(SQLModel):
    comments:List[ReviewReturn]
    next_cursor:Optional[int]

class BookReturn(SQLModel):
    id: int
    title: str
    author: AuthorBase
    published: int
    genres: list[GenreBase]
    rating:float
    rated:int
    
    class Config:
        from_attributes = True

class Rate(SQLModel):
    rate:int
    
class Activity(SQLModel, table=True):
    id :int =Field(default=None, primary_key=True)
    user_id: int=Field(foreign_key="userdb.id")
    book_id: str
    detail : str
    activity_type: str
    time: datetime=Field(default_factory=datetime.utcnow)
    
class ActivityReturn(SQLModel):
    id: int
    book_name:str
    detail:str
    