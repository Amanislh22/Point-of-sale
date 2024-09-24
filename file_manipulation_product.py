from collections import defaultdict
from datetime import datetime
import re
import uuid
from fastapi import Depends, HTTPException, status
from numpy import genfromtxt
from sqlalchemy import join
from enums import ContractType, Gender, Role
from enums.tokenStatus import TokenStatus
from file_manipulation import find_duplicates_in_file
from models import Employee
import aiofiles
from fastapi import Depends,status
from numpy import genfromtxt
from sqlalchemy import join
from enums import  ContractType, Gender, Role
from enums.tokenStatus import TokenStatus
from models.category import Category
from models.employee import Employee
from database import get_db
from sqlalchemy.orm import Session
import models
from models.accountActivation import AccountActivation
import models.company
from models.employeeRole import EmployeeRole
from models.product import Product
from models.customer import Customer
import schemas
from send_mail import  send_email
from sqlalchemy.exc import SQLAlchemyError
from error import add_error
import cloudinary
import cloudinary.uploader
import io
from Settings import setting

mandatory_fields_products = {
    "name": "name",
    "category_name": "category_name",
    "unit_price": "unit_price",
    "quantity": "quantity",
}

optional_fields_products = {
    "description": "description",
    "image_link": "image_link",
}

unique_fields_products = {
    "name": "name",
}

def validate_field_and_add_products(products, db: Session):
    products_to_add = []
    errors = []

    missing_mandatory_fields = set(mandatory_fields_products) - set(products[0].keys())
    if missing_mandatory_fields:
        missing_mandatory_fields = [
            field for field in missing_mandatory_fields]
        return schemas.ImportProductsResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message=f"Missing mandatory fields: {', '.join([field for field in missing_mandatory_fields])}"
        )


    duplicated_values = find_duplicates_in_file(products, unique_fields_products)
    for field, values in duplicated_values.items():
        if field in unique_fields_products:
            for value in values:
                errors.append(f"{field} should be unique. The value '{value}' is duplicated in the file.")


    if errors:
        return schemas.ImportProductsResponse(
            errors='\n'.join(errors),
            status=status.HTTP_400_BAD_REQUEST,
            message="Duplicated values in the file",
        )
    categories = db.query(Category).all()
    category_dict = {category.name: category for category in categories}
    for product_data in products:
        category_name = product_data['category_name']
        category = category_dict.get(category_name)
        product = Product(
        name=product_data['name'],
        category_id=category.id,
        unit_price=product_data['unit_price'],
        quantity=product_data['quantity'],
        description=product_data.get('description'),
        image_link=product_data.get('image_link')
        )
        products_to_add.append(product)

    product_list = [product.name for product in products_to_add]
    existing_products = db.query(models.Product).filter(models.Product.name.in_(product_list)).all()
    existing_names = {product.name for product in existing_products}

    for product in products_to_add:
        if product.name in existing_names:
            errors.append(f"product {product.name} already exists in the database.\n")

    if errors:
        return schemas.ImportProductsResponse(
            errors='\n'.join(errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        db.add_all(products_to_add)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return schemas.ImportProductsResponse(
            message='Database error occurred',
            status=status.HTTP_400_BAD_REQUEST
        )

    return schemas.ImportProductsResponse(
        message="Products added to the database",
        status=status.HTTP_200_OK
    )


