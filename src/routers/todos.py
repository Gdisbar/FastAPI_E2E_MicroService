from database import SessionLocal
from models import Todos
from fastapi import APIRouter
from typing import Annotated,Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path
from starlette import status
from .auth import get_current_user

router = APIRouter(
    # prefix="/todo",
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[Dict,Depends(get_current_user)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=5)
    description:str = Field(min_length=5,max_length=20)
    priority:int = Field(gt=0,lt=6)
    complete:bool

@router.get("/todo/",status_code=status.HTTP_200_OK)
async def get_all_todos(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="User not Authenticated")
    # get_current_user() returns : {"username":username,"user_id":user_id} 
    todos = db.query(Todos).filter(Todos.owner_id==user.get('user_id')).all()
    return todos

@router.get("/todo/{todos_id}",status_code=status.HTTP_200_OK)
async def get_todos_by_id(user:user_dependency,db:db_dependency,todos_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="User not Authenticated")
    todos = db.query(Todos).filter(Todos.owner_id==user.get('user_id')).filter(Todos.id == todos_id).first()
    if todos is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return todos

@router.post("/todo/",status_code=status.HTTP_201_CREATED)
async def create_todos(user:user_dependency,db:db_dependency,todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401,detail="User not Authenticated")
    todo_model = Todos(**todo_request.model_dump(),owner_id=user.get('user_id'))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todos(user:user_dependency,db:db_dependency,todo_request:TodoRequest,todos_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="User not Authenticated")
    todo_model = db.query(Todos).filter(Todos.owner_id==user.get('user_id')).filter(Todos.id == todos_id).first()
    if todo_model is None:
        return HTTPException(status_code=404,detail="Item not found")
    
    for field in todo_request.model_fields_set:
        setattr(todo_model, field, getattr(todo_request, field))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

@router.delete("/todo/{todos_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todos_by_id(user:user_dependency,db:db_dependency,todos_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="User not Authenticated")
    todos_model = db.query(Todos).filter(Todos.owner_id==user.get('user_id')).filter(Todos.id == todos_id).first()
    if todos_model is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.query(Todos).filter(Todos.owner_id==user.get('user_id')).filter(Todos.id == todos_id).delete()
    db.commit()
