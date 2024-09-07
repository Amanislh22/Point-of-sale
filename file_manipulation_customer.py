from fastapi import Depends, status
from numpy import genfromtxt
from sqlalchemy import join
from file_manipulation import find_duplicates_in_file
from fastapi import Depends,status
from numpy import genfromtxt
from sqlalchemy import join
from database import get_db
from sqlalchemy.orm import Session
import models
import models.company
from models.customer import Customer
import schemas
from send_mail import  send_email
from sqlalchemy.exc import SQLAlchemyError
from error import add_error
from Settings import setting
mandatory_fields_customer = {
    "name" : "name",
    "email" : "email",
}
unique_fields_customers={
    "email" : "email",
}

def validate_field_and_add_customers(customers , db:Session):
    customers_to_add=[]
    errors =[]

    missing_mandatory_fields = set(mandatory_fields_customer) - set(customers[0].keys())
    if missing_mandatory_fields:
        missing_mandatory_fields = [
            field for field in missing_mandatory_fields]
        return schemas.ImportCustomerResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message=f"Missing mandatory fields: {', '.join([field for field in missing_mandatory_fields])}"
        )
    duplicated_values = find_duplicates_in_file(customers, unique_fields_customers)
    for field, values in duplicated_values.items():
        for value in values:
            if field in unique_fields_customers:
                errors.append(f"{field} should be unique. The value '{value}' is duplicated in the file.")
    if errors:
            return schemas.ImportCustomerResponse(
            errors='\n'.join(errors),
            status=status.HTTP_400_BAD_REQUEST,
            message= " duplicated values in the file",
        )
    for customer_data in customers:
        customer = Customer(
            name=customer_data['name'],
            email=customer_data['email'],
        )
        customers_to_add.append(customer)

    email_list = [customer.email for customer in customers_to_add]
    existing_customer = db.query(models.Customer).filter(models.Customer.email.in_(email_list)).all()
    existing_emails = {customer.email for customer in existing_customer}

    for customer in customers_to_add:
        if customer.email in existing_emails:
            errors.append(f"Email {customer.email} already exists in the database.\n")

    if errors:
        return schemas.ImportCustomerResponse(
        errors='\n'.join(errors),
        status=status.HTTP_400_BAD_REQUEST,
        message= " customers already exist in the db",
    )

    try:
        db.add_all(customers_to_add)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        return schemas.ImportCustomerResponse(
            message='Database error occurred',
            status=status.HTTP_400_BAD_REQUEST,
        )
    return schemas.ImportCustomerResponse(
            message= "customers added to db",
            status = status.HTTP_200_OK, )
