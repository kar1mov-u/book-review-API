from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import users,books


app = FastAPI()

app.include_router(users.router)
app.include_router(books.router)



@app.on_event("startup")
def  on_startup():
    create_db_and_tables()
    
    
@app.get('/check')
def check():
    return {"data":"working"}