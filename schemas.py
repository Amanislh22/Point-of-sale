import json
from pydantic import BaseModel, model_validator
from typing import Dict, Optional, List, Union
from datetime import datetime
from pydantic import EmailStr
from enums import Role,Gender,AccountStatus,ContractType,TokenStatus
import enums
from models.product import Product
from enums.SessionStatus import SessionStatus

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

class CustomerIn(OurBaseModel):
    name : str
    email : EmailStr

class CustomerOut(OurBaseModelOut):
    name : Optional[str] = None
    email : Optional[EmailStr] = None

class CustomersOut(PagedResponse):
    list:Optional[List[CustomerOut]]=[]

class ImportCustomerResponse(OurBaseModelOut):
    name : Optional[str] = None
    email : Optional[EmailStr] = None
    errors: Optional[str]=None

class CategoryIn(OurBaseModel):
    id : int
    name : str
    description : str
    icon_name : str

class categoryOut(OurBaseModelOut):
    name :Optional[str] = None
    description : Optional[str] = None
    icon : Optional [str] = None

class categoriesOut(PagedResponse):
    list:Optional[List[categoryOut]]=[]

class productIn(OurBaseModel):
    id: int
    name : str
    category : str
    description : Optional[str] = None
    price : float
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class productOut(OurBaseModelOut):
    name : Optional[str]=None
    category : Optional[str] =None
    description : Optional[str] = None
    price : Optional[float] = None
    image_link : Optional[str] = None

class productsOut(PagedResponse):
    list: Optional[List[productOut]] = []

class ImportProductsResponse(OurBaseModelOut):
    name : Optional[str]=None
    category : Optional[str] =None
    description : Optional[str] = None
    price : Optional[float] = None
    image : Optional[str] = None
    errors: Optional[str]=None

class SessionOut (OurBaseModelOut):
    employee_id : Optional[int] =None
    openedAt : Optional[datetime] = None
    closedAt :  Optional[datetime] = None
    session_status : Optional[SessionStatus] = None

class SessionsOut(OurBaseModelOut):
    list: Optional[List[SessionOut]] = []

class productInput(OurBaseModel):
    id :int
    name: str
    quantity: int
    unit_price: float
class OrderIn(OurBaseModel):
    products : List[productInput]
    number : str
    customer_email : EmailStr
    created_on : datetime
    total_price : Optional[float] = None
    pricelist_name : Optional[str] = None
    discount_code : Optional[str] =None


class orderLineOut(OurBaseModelOut):
    products : Optional[List[productInput]] = []
    total_price : Optional[float] = None

class orderlinesOut(OurBaseModelOut):
    list :Optional[List[orderLineOut]] = []
    total_price : float

class orderOut(OurBaseModelOut):
    session_id:int
    date : datetime
    receipt_number : str
    employee : str
    customer : Optional[str]=None
    total : float
    lines : List[orderLineOut]

class ordersOut(OurBaseModelOut):
     list: Optional[List[orderOut]] = []

class PricelistIn(OurBaseModel):
    name : str
    description : str

class pricelistOut(OurBaseModelOut):
    name : Optional[str] = None
    description : Optional[str] = None

class pricelistsOut(PagedResponse):
    list:Optional[List[pricelistOut]]=[]

class PricelistLine(OurBaseModel):
    pricelist_name : str
    product_name : str
    new_price : float
    min_quantity : int
    start_date : datetime
    end_date : datetime

class pricelistLineOut(OurBaseModelOut):
    pricelist_name : Optional[str] = None
    product_name :  Optional[str] = None
    new_price :  Optional[float] = None
    min_quantity :  Optional[int] = None
    start_date :  Optional[datetime] = None
    end_date : Optional[datetime] = None

class pricelistlinesOut( PagedResponse):
    list:Optional[List[pricelistLineOut]]=[]

class ProgramIn(OurBaseModel):
    name : str
    description : str
    program_type: enums.ProgramType
    discount : Optional[float] = None
    start_date : datetime
    end_date : datetime
    product_buy_id : Optional[int] =  None
    product_get_id : Optional[int] = None
    count : Optional[int] = None

class ProgramOut(OurBaseModelOut):
    name : Optional[str]= None
    description : Optional[str]= None
    program_type: Optional[enums.ProgramType] = None
    discount : Optional[float] = None
    start_date : Optional[datetime]= None
    end_date : Optional[datetime]= None
    product_buy_id : Optional[int] =  None
    product_get_id : Optional[int] = None

class ProgramsOut(PagedResponse):
    list:Optional[List[ProgramOut]]

class ProgramItemOut(OurBaseModelOut):
    code : Optional[str]= None
    code_status : Optional[enums.codeStatus] = None
    program_id : Optional[int] = None
    order_id : Optional[int] =None

class ProgramItemsOut(OurBaseModelOut):
    list: Optional[List[ProgramItemOut]] = None













