from fastapi import FastAPI
from routers import auth, user
from database import engine, Base
Base.metadata.create_all(bind=engine)
app = FastAPI()




