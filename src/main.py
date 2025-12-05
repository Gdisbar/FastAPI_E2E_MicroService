from database import engine,SessionLocal
from models import Todos
from fastapi import FastAPI
from models import Base
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from starlette import status

from routers import auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

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
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()



@app.put("/todo/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todos(db:db_dependency,todo_request:TodoRequest,todos_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todos_id).first()
    if todo_model is None:
        return HTTPException(status_code=404,detail="Item not found")
    
    for field in todo_request.model_fields_set:
        setattr(todo_model, field, getattr(todo_request, field))
    
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

@app.delete("/todo/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todos_by_id(db:db_dependency,todos_id:int=Path(gt=0)):
    todos_model = db.query(Todos).filter(Todos.id == todos_id).first()
    if todos_model is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.query(Todos).filter(Todos.id == todos_id).delete()
    db.commit()
