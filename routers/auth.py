from fastapi import Depends, Query, status ,File
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models
import schemas
from datetime import datetime, timedelta
from security import  get_hashed_password , verify_password , create_access_token
import security
from send_mail import send_email
import uuid
import enums

from fastapi import APIRouter
router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)
@router.post("/login", response_model=schemas.Token)
def login_user(employee_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(models.Employee).filter(models.Employee.email == employee_credentials.username).first()

        if not user:
            return schemas.Token(
                status_code = status.HTTP_400_BAD_REQUEST,
                message = "User not found in db "

            )

        if user.status == enums.AccountStatus.inactive:
            return schemas.Token(
                status_code = status.HTTP_403_FORBIDDEN,
                message = "Email has not been verified yet"
            )

        if not verify_password(employee_credentials.password, user.password):
            return schemas.Token(
                status_code=status.HTTP_400_BAD_REQUEST,
                message =  "Did you forget your password?"
            )

        role_names = [role.role for role in user.roles]

        employee_data = {
            "employee": {
                "id": user.id,
                "email": user.email
            },
            "roles": role_names
        }

        access_token = create_access_token(employee_data, timedelta(minutes=20))
    except Exception as e:
        return schemas.Token(
            message= "An unexpected error occurred",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        status=status.HTTP_200_OK
    )

@router.post("/logout")
def logout(token:str=Depends(security.oauth2_scheme),db: Session= Depends(get_db)):
    try:
        jwtBlacklist_entry = models.jWTBlacklist.JWTBlacklist(token=token)
        db.add(jwtBlacklist_entry)
        db.commit()
    except SQLAlchemyError as e:
        return schemas.BlacklistTokenOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong"
        )
    return schemas.BlacklistTokenOut(
        status=status.HTTP_200_OK,
        message="Logged out successfully"
    )

@router.post("/setpsw",response_model=schemas.SetPasswordOut)
async def set_psw (setpsw: schemas.SetPsw ,db: Session = Depends(get_db),token: str = Query(...),):
    try:
        account_activation_entry = db.query(models.AccountActivation).filter(models.AccountActivation.token == token).first()
    except Exception :
        return schemas.SetPasswordOut(
            message=" db error occured",
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not account_activation_entry:
        return schemas.SetPasswordOut(
                message='Invalid token',
                status=status.HTTP_404_NOT_FOUND
            )
    if account_activation_entry.created_on +  timedelta(minutes=60) < datetime.now():
        return schemas.SetPasswordOut(
                message='Token has expired',
                status=status.HTTP_400_BAD_REQUEST
            )

    if account_activation_entry.status == enums.TokenStatus.used:
        return schemas.SetPasswordOut(
                message='Token used',
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        user = db.query(models.Employee).filter(models.Employee.id == account_activation_entry.employee_id).first()
    except Exception :
        return schemas.SetPasswordOut(
            message=" db error occured",
            status=status.HTTP_400_BAD_REQUEST,
        )
    if(setpsw.password != setpsw.confirm_psw):
        return schemas.SetPasswordOut(
                message='Passwords do not match',
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        try:
            updates = {
                "password": get_hashed_password(setpsw.password),
                "status": enums.AccountStatus.active, }
            db.query(models.Employee).filter(models.Employee.id == user.id).update(updates)
            account_activation_entry.status = enums.TokenStatus.used
            db.commit()
            db.refresh(user)
            return schemas.SetPasswordOut(
                message="password set successfly",
                status= status.HTTP_200_OK
            )
        except Exception as e :
            db.rollback()
            return schemas.SetPasswordOut(
                message= "something went wrong ",
                status=status.HTTP_400_BAD_REQUEST
            )

@router.post("/forgotpsw", response_model=schemas.ForgotPasswordOut)
async def forgot_psw(request: schemas.forgotpsw, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.Employee).filter(models.Employee.email == request.email).first()

        if not existing_user:
                return schemas.ForgotPasswordOut(
                    message='No account with this email',
                    status=status.HTTP_404_NOT_FOUND
                )
        if existing_user.status == enums.AccountStatus.inactive:
            return schemas.ForgotPasswordOut(
                    message='User inactive ',
                    status=status.HTTP_400_BAD_REQUEST
                )

        new_entry = models.ChangePassword(
                        employee_id=existing_user.id,
                        token= uuid.uuid4(),
                        created_on= datetime.now()+timedelta(hours=12),
                        status= enums.TokenStatus.pending,)
        db.add(new_entry)
        db.flush()
        token = new_entry.token

        await send_email("reset psw ", existing_user.email, token)

        db.commit()
        return schemas.ForgotPasswordOut(
                message='Email sent successfully',
                status=status.HTTP_200_OK
                )

    except Exception as e:
        db.rollback()
        return schemas.ForgotPasswordOut(
            message="An error occurred while processing the request",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post('/change-password', response_model=schemas.ChangePasswordOut)
def change_password(request: schemas.change_password, db: Session = Depends(get_db),token: str = Query(...),):
    try:
        change_password_entry = db.query(models.ChangePassword).filter(models.ChangePassword.token == token).first()
        if not change_password_entry:
            return schemas.ChangePasswordOut(
                    message='Invalid token',
                    status=status.HTTP_404_NOT_FOUND
                )

        if change_password_entry.created_on + timedelta(minutes=60) < datetime.now():
            return schemas.ChangePasswordOut(
                    message='Token has expired',
                    status=status.HTTP_400_BAD_REQUEST
                )

        if change_password_entry.status == enums.TokenStatus.used :
            return schemas.ChangePasswordOut(
                    message='Token used',
                    status=status.HTTP_400_BAD_REQUEST
                )

        user = db.query(models.Employee).filter(models.Employee.id == change_password_entry.employee_id).first()
        if not verify_password(request.old_password,user.password) :
            return schemas.ChangePasswordOut(
                    message='Invalid old password',
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            user.password=get_hashed_password(request.new_password)
            change_password_entry.status = enums.TokenStatus.used
            db.commit()
            db.refresh(user)
            return schemas.ChangePasswordOut(
                    message='Password changed successfully',
                    status=status.HTTP_200_OK
                )
    except Exception as e :
            db.rollback()
            return schemas.SetPasswordOut(
                message= "db error occured ",
                status=status.HTTP_400_BAD_REQUEST,
            )


