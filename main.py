from fastapi import FastAPI
from routers import auth, user,company,customer,category, product, session, order, pricelist, program
from database import engine, Base
from firebase_admin import credentials, initialize_app
import firebase_admin
from firebase_admin import credentials



Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(company.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(customer.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(session.router)
app.include_router(order.router)
app.include_router(pricelist.router)
app.include_router(program.router)




