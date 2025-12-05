from database import engine,SessionLocal
from models import Todos
from fastapi import FastAPI
from models import Base
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from starlette import status


app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=5)
    description:str = Field(min_length=5,max_length=20)
    priority:int = Field(gt=0,lt=6)
    complete:bool

@app.get("/todo/",status_code=status.HTTP_200_OK)
async def get_all_todos(db:db_dependency):
    todos = db.query(Todos).all()
    return todos

@app.get("/todo/{todos_id}",status_code=status.HTTP_200_OK)
async def get_todos_by_id(db:db_dependency,todos_id:int=Path(gt=0)):
    todos = db.query(Todos).filter(Todos.id == todos_id).first()
    if todos is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return todos

@app.post("/todo/",status_code=status.HTTP_201_CREATED)
async def create_todos(db:db_dependency,todo_request:TodoRequest):
    todo_data = Todos(**todo_request.model_dump())
    db.add(todo_data)
    db.commit()
    return f"Data insterd to DB"