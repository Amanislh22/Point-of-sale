from fastapi import FastAPI
from routers import auth, company, user
from database import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(company.router)
app.include_router(auth.router)
app.include_router(user.router)
