import codecs
from fastapi import Depends, Form, Query, status, File, UploadFile
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from enums.tokenStatus import TokenStatus
from error import add_error, get_error_message
from file_manipulation import is_valid_cnss, validate_fields_and_add_employees, validate_fields_and_add_employees, mandatory_fields
import models
from security import get_current_user
from enums import AccountStatus
from models.accountActivation import AccountActivation
from models.employee import Employee
from models.employeeRole import EmployeeRole
import schemas, csv
from datetime import datetime
from send_mail import send_email
import uuid
from enums import Role
from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from error import error_keys

router=APIRouter(
    prefix="/employees",
    tags=["employees"]
)
#current_user=Depends(get_current_user([Role.admin, Role.super_user]))
@router.post("/add", response_model=schemas.EmployeeOut)
async def add_user(user: schemas.Employee, company_id :int, db: Session = Depends(get_db),):
    employee_role_obj=[]
    try:
        company = db.query(models.Company).filter(models.Company.id==company_id).first()
        if not company:
                return schemas.EmployeeOut(
                    message="Company not found",
                    status=404
                )
        employee_code = company.last_employee_number
        employee_code += 1
        new_user = Employee(firstname= user.firstname,
                                email= user.email,
                                password= None,
                                status= AccountStatus.inactive,
                                lastname= user.lastname,
                                number= employee_code,
                                phone_number= user.phone_number,
                                cnss_number= user.cnss_number,
                                birth_date= user.birth_date,
                                gender= user.Gender,
                                contract_type= user.contract_type,
                                company_id = company_id
                                )
        db.add(new_user)
        db.flush()

        for role in user.roles:
            new_role = EmployeeRole(employee_id= new_user.id,
                                    role= role)
            employee_role_obj.append(new_role)

        db.add_all(employee_role_obj)
        db.flush()

        new_account = AccountActivation(employee_id=new_user.id,
                                            token= uuid.uuid4(),
                                            created_on= datetime.now(),
                                            status=TokenStatus.pending,
                                            email=user.email)

        db.add(new_account)
        token = new_account.token
        await send_email("Account Activation", user.email, token)

        company.last_employee_number = employee_code
        db.commit()
        return schemas.EmployeeOut(
                message='User created successfully. Please check your email to activate your account',
                status=status.HTTP_201_CREATED
            )

    except SQLAlchemyError as e:
        db.rollback()
        add_error(e,db)
        return schemas.EmployeeOut(
            message = get_error_message(str(e.__dict__['orig']), error_keys),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/upload", response_model=schemas.ImportEmployeeResponse)
async def upload(
        file: UploadFile = File(...),
        company_id: int = Form(...),
        force_upload: bool = Form(False),
        db: Session = Depends(get_db)):

    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    employees = list(csv_reader)

    if not employees:
        return schemas.ImportEmployeeResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message="Could not import empty file"
        )
    company_query = db.query(models.Company).filter(models.Company.id==company_id)
    company = company_query.first()
    if not company:
        return schemas.ImportEmployeeResponse(
            message="Company not found",
            status=status.HTTP_404_NOT_FOUND
        )

    missing_mandatory_fields = set(mandatory_fields) - set(employees[0].keys())
    if missing_mandatory_fields:
        missing_mandatory_fields = [
            field for field in missing_mandatory_fields]
        return schemas.ImportEmployeeResponse(
            status=status.HTTP_400_BAD_REQUEST,
            message=f"Missing mandatory fields: {', '.join([field for field in missing_mandatory_fields])}"
        )

    return  await validate_fields_and_add_employees(employees, company_id,force_upload, db)


@router.post("/",response_model=schemas.EmployeeOut)
def get_user_by_id(id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user([Role.admin, Role.super_user]))):
    empl = db.query(Employee).filter(Employee.id==id).first()
    if not empl:
        return schemas.EmployeeOut(
            message=f'empployee with is {id} not found',
            status=status.HTTP_404_NOT_FOUND
        )
    return schemas.EmployeeOut(id=empl.id,lastname=empl.lastname,firstname=empl.firstname,roles=empl.roles,Gender=empl.gender,
                               message=f'user with id {id}',
                               status=status.HTTP_200_OK)


@router.post("/",response_model=schemas.EmployeesOut)
def get_all_users(total_pages : int , total_records : int,page_number : int ,page_size:int , db: Session = Depends(get_db)  ,current_user=Depends(get_current_user([Role.admin, Role.super_user]))):
    employees =  db.query(Employee).all()
    return schemas.EmployeeOut(
        total_pages = total_pages,
        total_records = total_records,
        page_number = page_number,
        page_size = page_size,
        list=employees )


@router.post("/", response_model=schemas.EmployeeOut)
def deactivate(email: str = Query(...), db: Session = Depends(get_db),current_user=Depends(get_current_user([Role.admin, Role.super_user]))):
    try:
        user = db.query(Employee).filter(Employee.email == email).first()
        if not user:
            return schemas.EmployeeOut(
                    message='User not found',
                    status=status.HTTP_404_NOT_FOUND
                )

        if (user.status == AccountStatus.inactive):
            return schemas.EmployeeOut(
                    message='user already inactive ',
                    status=status.HTTP_400_BAD_REQUEST
                )
        else :
            user.status= AccountStatus.inactive
            db.commit()
            return schemas.EmployeeOut(
                    message='user deactivated succ',
                    status=status.HTTP_200_OK
                )
    except Exception as e:
        return schemas.Token(
            message= "An unexpected error occurred",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


