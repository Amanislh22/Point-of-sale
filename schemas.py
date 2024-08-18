from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
from pydantic import EmailStr
from enums import Role,Gender,AccountStatus,ContractType,TokenStatus

class OurBaseModel(BaseModel):
    class Config:
        orm_mode=True

class OurBaseModelOut(OurBaseModel):
    message :Optional[str]=None
    status :Optional[int]=None

class Employee(BaseModel):
    id: Optional[int]
    firstname:str
    lastname:str
    number:Optional[int]
    Gender:Gender
    roles: list[Role]
    phone_number :str
    status : AccountStatus
    email : EmailStr
    cnss_number:str
    contract_type :ContractType
    birth_date :datetime
    password:str

class EmployeeRole(BaseModel):
    id:int
    employee_id:int
    role : Role

class change_password(BaseModel):
    old_password:str
    new_password:str

class account_activation(BaseModel):
    id:int
    email:str
    token:str
    status:TokenStatus
    expiration_date:datetime
    employee_id:int

class SetPsw(OurBaseModel):
    password:str
    confirm_psw :str

class forgotpsw(BaseModel):
    email:EmailStr

class login(BaseModel):
    email:str
    password:str

class ForgotPasswordOut(BaseModel):
    message:str
    status:int

class SetPasswordOut(BaseModel):
    message:str
    status:int

class ChangePasswordOut(BaseModel):
    message:str
    status:int

class EmployeeOut(OurBaseModelOut):
    id:Optional[int]=None
    roles:Optional[List[Role]]=None
    firstname:Optional[str]=None
    lastname:Optional[str]=None
    gender:Optional[Gender]=None
    phone:Optional[str]=None
    total_pages :Optional[int]=None
    total_records:Optional[int]=None
    page_number :Optional[int]=None
    page_size :Optional[int]=None
    list : Optional[Employee]=None

class Token(OurBaseModelOut):
    access_token :Optional[str] =None
    token_type:Optional[str] =None

class TokenData(OurBaseModel):
    id:Optional[int] = None

class BlacklistTokenOut(BaseModel):
    status:int
    message: str

class JWTBlacklist(BaseModel):
    token:str

class PagedResponse(OurBaseModelOut):
    page_number:Optional[int]=None
    page_size:Optional[int]=None
    total_pages:Optional[int]=None
    total_records:Optional[int]=None

class EmployeesOut(PagedResponse):
    list:Optional[List[EmployeeOut]]=[]

class ValidationResult(OurBaseModelOut):
    errors: Optional[List[str]]=None
    warnings: Optional[List[str]]=None
    employees : Optional[List[dict]]=None

class ImportEmployeeResponse (OurBaseModelOut):
    errors: Optional[str]=None
    warnings: Optional[str]=None
    employees: Optional[List[Dict[str, str]]] = None

class Company(OurBaseModel):
    name: str
    last_employee_number : int
    id : int

class CompanyOut(OurBaseModelOut):
    id: Optional[int] = None
    name: Optional[str] = None
    last_employees_code: Optional[int] = None

class ErrorOut(OurBaseModelOut):
    id: Optional[int] = None
    orig: Optional[str] = None
    params: Optional[str] = None
    statement: Optional[str] = None
    created_at: Optional[datetime] = None
