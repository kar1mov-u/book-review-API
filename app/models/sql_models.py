from sqlmodel import SQLModel,Field


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
    