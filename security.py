from datetime import datetime, timedelta,timezone
from typing import Optional
from database import get_db
from jose import JWTError, jwt
from Settings import setting
from passlib.context import CryptContext
from fastapi import Depends, HTTPException,status
import enums
from error import add_error
import models
from models.employee import Employee
import schemas
import Settings
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_
from models.employee import Employee

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings.setting.SECRET_KEY, algorithm=Settings.setting.ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str , db : Session= Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"------Counld not validate credentials",
        headers={"WWW.Authenticate": "Bearer"}
    )
    blacklisted_token = db.query(models.JWTBlacklist).filter(models.JWTBlacklist.token == token).first()
    if blacklisted_token:
        raise credentials_exception
    try:
        payload = jwt.decode(token , Settings.setting.SECRET_KEY, algorithms=[Settings.setting.ALGORITHM])
        id: str = payload["employee"]["id"]
        if id is None:
            raise credentials_exception
        token_data= schemas.TokenData(id=id)
    except JWTError :
        return credentials_exception

    return token_data

def get_current_user(roles=[enums.role]):
    def _get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_data = verify_access_token(token, db)
        employee = db.query(Employee).filter(
            and_(
                models.Employee.id == token_data.id,
                models.Employee.password != None,
                models.Employee.status == enums.accountStatus.AccountStatus.active,
            )
        ).first()
        if not employee:
            raise credentials_exception

        employee_role = db.query(models.EmployeeRole).filter(
            and_(
                models.EmployeeRole.employee_id == token_data.id,
                models.EmployeeRole.role.in_(roles),
            )
        ).first()
        if not employee_role:
            raise HTTPException(
                detail="You don't have permission to access this",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return employee

    return _get_current_user

