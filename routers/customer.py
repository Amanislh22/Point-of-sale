import codecs
from fastapi import Depends, Form, Query , status ,File , UploadFile
from pydantic import EmailStr
from database import engine , SessionLocal, get_db
from sqlalchemy.orm import Session
from error import get_error_message, error_keys
from file_manipulation_customer import validate_field_and_add_customers , mandatory_fields_customer
from security import get_current_user
import schemas, csv
from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
import models
import utils
import enums

router=APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.post("/add", response_model=schemas.CustomerOut)
async def add_customer(customer: schemas.CustomerIn, db: Session = Depends(get_db),current_customer=Depends(get_current_user([enums.Role.admin, enums.Role.super_user]))):
    try:
        new_customer = models.Customer(name= customer.name,
                                    email= customer.email,
                                    )
        db.add(new_customer)
        db.flush()
        db.commit()
        return schemas.CustomerOut(
            message='customer added successfully',
            status=status.HTTP_201_CREATED,)
    except SQLAlchemyError as e:
        db.rollback()
        return schemas.CustomerOut(
            message = get_error_message(str(e.__dict__['orig']), error_keys),
            status=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/edit", response_model=schemas.CustomerOut)
async def edit_customer(customer: schemas.CustomerIn,email:EmailStr, db: Session = Depends(get_db),):
    try:
        existing_customer = db.query(models.Customer).filter_by(email=email).first()

        if not existing_customer:
            return schemas.CustomerOut (
                message="customer not found",
                status=status.HTTP_400_BAD_REQUEST,)


        existing_customer.email = customer.email
        existing_customer.name = customer.name

        db.commit()

        return schemas.CustomerOut(
            message='customer edited successfully.',
            status=status.HTTP_201_CREATED,)

    except SQLAlchemyError as e:
        db.rollback()
        return schemas.CustomerOut(
            message='Database error occurred',
            status=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/upload", response_model=schemas.ImportCustomerResponse)
async def upload(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)):

    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    customers = list(csv_reader)

    if not customers:
        return schemas.ImportCustomerResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message="Could not import empty file",
        )

    return  validate_field_and_add_customers(customers, db)

@router.post("/getall",response_model=schemas.CustomersOut)
def get_all_customers(page_number : int ,page_size:int , name_filter: str = None, db: Session = Depends(get_db) ):
    try:
        if name_filter:
            customer =  db.query(models.Customer).filter_by(name=name_filter)
        else :
            customer =  db.query(models.Customer)

        total_records = db.query(models.Customer).count()
        total_pages = utils.div_ceil(total_records,page_size)
        customers = customer.offset((page_number-1) * page_size).limit(page_size).all()

        return schemas.CustomersOut(
            total_records = total_records,
            total_pages = total_pages,
            page_number = page_number,
            page_size = page_size,
            list = [ schemas.CustomerOut(**customer.__dict__) for customer in customers],
            status=status.HTTP_200_OK, )
    except Exception :
        return schemas.CustomersOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )
