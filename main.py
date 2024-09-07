from fastapi import FastAPI
from routers import auth, user,company,customer,category, product, session, order
from database import engine, Base
from firebase_admin import credentials, initialize_app
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("/home/ameni/Downloads/pos-project-8d951-firebase-adminsdk-u3f4p-ef9f3961c5.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://pos-project-8d951.appspot.com'
})

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




