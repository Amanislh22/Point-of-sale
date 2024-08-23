import schemas, models
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status

error_keys = {
       "unique_email_constraint" : "this email is already used",
       "unique_cnss_number" : "this cnss number already exists",
       "unique_email_customer_constraint" : "this eamil  is already used"}

def add_error(e: SQLAlchemyError, db: Session = Depends(get_db)):
    error = models.Error(
        orig=str(e.__dict__['orig']),
        params=str(e.__dict__['params']),
        statement=str(e.__dict__['statement'])
    )
    try:
        db.add(error)
        db.commit()
        db.refresh(error)
    except Exception as e:
        db.rollback()
        return schemas.ErrorOut(
            status = status.HTTP_500_INTERNAL_SERVER_ERROR,
            message = str(e)
        )
    return schemas.ErrorOut(**error.__dict__, status = status.HTTP_201_CREATED, message = "Error created successfully")

def get_error_message(error_message, error_keys):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key]

    return "Something went wrong"


