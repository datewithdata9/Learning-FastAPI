from fastapi import FastAPI,HTTPException,Depends,Path,Body
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status

from pydantic import BaseModel,Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# async def get_db():
#     async with SessionLocal() as session:
#         yield session

def get_db():
    with SessionLocal() as session:
        yield session

db_dependency = Annotated[Session, Depends(get_db)]


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3,max_length=100)
    priority: int = Field(gt=0,lt=6)
    complete: bool


@app.get('/')
async def get_todos(db: db_dependency):
    return db.query(models.Todos).all()

@app.get('/todo/{todo_id}',status_code=status.HTTP_200_OK)
async def get_todoid(db: db_dependency,todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail='ToDo Not Found')

@app.post('/todo/',status_code=status.HTTP_201_CREATED)
async def add_todos(db: db_dependency, todo_request: ToDoRequest):
    todo_model = models.Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()

@app.put('/todo/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,todo_request: ToDoRequest,todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id==todo_id).first()
    if todo_model is None:
        return HTTPException(status_code=404,detail='To Do Not Found')

    for key, value in vars(todo_request).items():
        setattr(todo_model, key, value)
    
    #  you don't need to call db.add() explicitly for objects that are already being tracked by the session.
    #db.add(todo_model)
    db.commit()

@app.delete('/todo/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        return HTTPException(status_code=404,detail='To Do Not Found')
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()