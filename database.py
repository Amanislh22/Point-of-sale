from fastapi import Depends, HTTPException , status
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from Settings import setting


DATABASE_URL = (
    f"postgresql://{setting.POSTGRES_USER}:{setting.PASSWORD_POSTGRES}"
    f"@{setting.POSTGRES_HOSTNAME}/{setting.POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
Base =declarative_base()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




import models

