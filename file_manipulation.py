from collections import defaultdict
from datetime import datetime
import re
import uuid
from fastapi import Depends, status
from numpy import genfromtxt
from sqlalchemy import join
from enums import ContractType, Gender, Role
from enums.tokenStatus import TokenStatus
from models import Employee
from fastapi import Depends,status
from numpy import genfromtxt
from sqlalchemy import join
from enums import  ContractType, Gender, Role
from enums.tokenStatus import TokenStatus
from models.employee import Employee
from database import get_db
from sqlalchemy.orm import Session
import models
from models.accountActivation import AccountActivation
import models.company
from models.employeeRole import EmployeeRole
import schemas
from send_mail import  send_email
from sqlalchemy.exc import SQLAlchemyError
from error import add_error
from Settings import setting

mandatory_unique_fields = {
    "email" : "email"
}
mandatory_fields = {
    'firstname':'firstname',
    'lastname':'lastname',
    'roles' : 'roles',
    'contract_type' : 'contract_type',
    'gender' : 'gender',
    **mandatory_unique_fields
}

optional_fields = {
     'phone_number': 'phone_number',
     'birth_date' : 'birth_date' ,
     "cnss_number" :  "cnss_number"
}

mandatory_unique_fields_per_contract = {
"cnss_number": "cnss_number",
}

unique_fields = [
    *mandatory_unique_fields,
    *mandatory_unique_fields_per_contract,
]

possible_fields = {
    **mandatory_fields,
    **optional_fields,
}

model_field_by_field_name = {
    "cnss_number": Employee.cnss_number,
    "email": Employee.email,
}
mandatory_unique_fields = {
    "mandatory_unique_fields" : mandatory_unique_fields,
    "mandatory_unique_fields_per_contract" : mandatory_unique_fields_per_contract,


}

CNSS_REGEX = re.compile(r'^\d{8}-\d{2}$')

def is_regex_matched(regex,field):
     return field if re.match(regex,field) else None

def is_valid_date(date_str):
    try:
        obj = datetime.strftime(date_str,"%m-%d-%y")
        return obj.isformat()
    except Exception as e:
        return None

def isCdiOrCdd(contract_type):
    return contract_type.strip().lower() in [ContractType.cdd, ContractType.cdi]

def is_valid_cnss(employee, field):
    contract = employee.get("contract_type")
    if not contract:
        return None
    if isCdiOrCdd(contract):
        return field if field and is_regex_matched(CNSS_REGEX,field) else None
    elif not isCdiOrCdd(contract):
        return field if field is None or is_regex_matched(CNSS_REGEX,field) else None
    return None

def are_valid_jobs(field):
    roles = field.split(";")
    if all(Role.is_valid_enum_value(role.strip()) for role in roles):
            return roles
    return None

check_field = {
    "birth_date": (lambda employee, birth_date: is_valid_date(birth_date), "Date should be in format DD-MM-YYYY"),
    "contract_type": (lambda employee, contract_type: ContractType.is_valid_enum_value(contract_type), "Contract type should be on of CDI,CDD,SIVP,Apprenti"),
    "gender": (lambda employee, gender: Gender.is_valid_enum_value(gender), "Gender should be on of Male,Female"),
    "roles": (lambda employee, roles: are_valid_jobs(roles), "Values should be admin ,vendor,inventory manager"),
    "cnss_number": (lambda employee, cnss_number: is_valid_cnss(employee,cnss_number), "CNSS should be {8 digits}-{2 digits} and it's mandatory only for Cdi and Cdd"),
}

def validate_employee_input(employee: dict, employees_to_add: list=[]):
    errors=[]
    warnings= []
    employee_to_add = dict(employee)

    for field in possible_fields:
        if field not in employee_to_add :
            continue
        employee_to_add[field] = employee_to_add[field].strip()
        if employee_to_add[field] == "" :
            if field in mandatory_fields:
                errors.append(f"{field} is missing despite its mandatory")
            else:
                employee_to_add[field] = None
        elif field in check_field:
            converted_value = check_field[field][0](
                employee_to_add, employee_to_add[field]
            )
            if converted_value is None:
                (errors if field in mandatory_fields else warnings).append(
                    f"{employee_to_add[field]} is not good value.{check_field[field][1]}")
            employee_to_add[field] = converted_value

    employees_to_add.append(employee_to_add)

    return schemas.ImportEmployeeResponse(
        errors = '\n'.join(errors),
        warnings= '\n'.join(warnings),
        status=status.HTTP_400_BAD_REQUEST if (errors or warnings) else status.HTTP_200_OK,
    )

def find_duplicates_in_file(employees, unique_fields):
    duplicated_values = defaultdict(set)
    values_set = set()
    for field in unique_fields:
        for employee in employees:
            value = employee[field].strip()
            if value == '':
                continue
            if value in values_set:
                duplicated_values[field].add(value)
            else:
                values_set.add(value)

    return {field: list(values) for field, values in duplicated_values.items()}

async def validate_fields_and_add_employees(employees: list, company_id :int,  force_upload, db:Session):
    errors = []
    warnings = []
    employees_to_add =[]

    for line, employee in enumerate(employees):
        employee_validation = validate_employee_input(employee, employees_to_add)
        if employee_validation.status != status.HTTP_200_OK:
            if employee_validation.errors:
                errors.append(f'Line {line} :\n{employee_validation.errors}\n')
            if employee_validation.warnings:
                warnings.append(f'Line {line}:\n{employee_validation.warnings}\n')

    duplicated_values = find_duplicates_in_file(employees, unique_fields)
    for field, values in duplicated_values.items():
        for value in values:
            if field in mandatory_unique_fields:
                errors.append(f"{field} should be unique. The value '{value}' is duplicated in the file.")


    email_list = [employee['email'] for employee in employees_to_add]
    existing_users = db.query(Employee).filter(Employee.email.in_(email_list)).all()
    existing_emails = {user.email for user in existing_users}
    for employee in employees_to_add:
        if employee['email'] in existing_emails:
            errors.append(f"Email {employee['email']} already exists in the database.")

    if errors or (warnings and not force_upload):
        return schemas.ImportEmployeeResponse(
            errors='\n'.join(errors),
            warnings='\n'.join(warnings),
            status=status.HTTP_400_BAD_REQUEST,
        )

    employee_per_code = {}
    employee_roles_per_employee_code= defaultdict(list)
    employee_roles = []
    account_activation =[]
    company_query = db.query(models.Company).filter(models.Company.id==company_id)
    company = company_query.first()
    employee_code = company.last_employee_number
    try:
        for employee in employees_to_add:
            employee_code+=1
            employee_jobs = employee["roles"]
            for job in employee_jobs:
                employee_roles_per_employee_code[employee_code].append(job.strip())
            employee.pop("roles")
            employee["number"] = employee_code
            employee_per_code[employee_code] = employee

        for code, employee in employee_per_code.items():
            employee_per_code[code] = Employee(**employee, company_id=company_id)
        db.add_all(employee_per_code.values())
        db.flush()
        employee_roles = [
        EmployeeRole(employee_id=employee_per_code[code].id, role=role_name)
        for code, roles in employee_roles_per_employee_code.items()
        for role_name in roles]
        db.add_all(employee_roles)

        for code , employee in employee_per_code.items():
            token=uuid.uuid4()
            account_activation.append(AccountActivation(
            employee_id = employee_per_code[code].id,
            token= token,
            created_on= datetime.now(),
            status=TokenStatus.pending,
            email=employee_per_code[code].email))

            await send_email("account confirmation" , employee_per_code[code].email, token)

        db.add_all(account_activation)

        company.last_employee_number =employee_code
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        add_error(e,db)
        return schemas.EmployeeOut(
            message="Database error occurred",
            status=status.HTTP_400_BAD_REQUEST,
        )
    return schemas.ImportEmployeeResponse(
            message= "employees added to db and mail sent ",
            status = status.HTTP_200_OK,)






