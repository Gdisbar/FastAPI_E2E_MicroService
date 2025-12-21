from database import engine
from models import Base
from routers import auth,todos,admin
# from src.models import Base
# from src.routers import auth, todos, admin
# from src.database import engine

from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)