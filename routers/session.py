from datetime import datetime
from fastapi import APIRouter, Depends , status
from database import get_db
from enums import Role
from enums.SessionStatus import SessionStatus
from error import add_error
import models
from models.employee import Employee
from models.employeeRole import EmployeeRole
from models.session import Session as modelSession
from sqlalchemy.orm import Session
import schemas
from security import get_current_user
import utils
from enums.SessionAction import SessionAction
from enums.SessionStatus import SessionStatus

router=APIRouter(
    prefix="/sessions",
    tags=["sessions"]
)

@router.get("/onOffSession" , response_model=schemas.SessionOut)
def session_action(action : str, db: Session = Depends(get_db)  ,current_user=Depends(get_current_user([Role.vendor, Role.super_user]))):
    try:
        if action == SessionAction.start:
            session_record = db.query(modelSession).filter_by(session_status=SessionStatus.open , employee_id=current_user.id).first()
            if session_record :
                return schemas.SessionOut(
                    message = " only one session can be open per employee ",
                    status=status.HTTP_400_BAD_REQUEST
                )
            else :
                new_session = modelSession(opened_at= datetime.utcnow(),
                                    closed_at = None,
                                    employee_id = current_user.id,
                                    session_status = SessionStatus.open)

                db.add(new_session)
                db.commit()
                return schemas.SessionOut(
                        message="session started ",
                        status=status.HTTP_200_OK
                    )

        elif action == SessionAction.end:
            session_record = db.query(modelSession).filter_by(session_status=SessionStatus.open).first()
            if session_record and session_record.employee_id == current_user.id:
                session_record.session_status = SessionStatus.closed
                session_record.closed_at = datetime.utcnow()
                db.commit()
                return schemas.SessionOut(
                    message="session ended ",
                    status=status.HTTP_200_OK
                )
            else :
                return schemas.SessionOut(
                    message=" you can't end the session ",
                    status=status.HTTP_400_BAD_REQUEST,
                )
    except Exception as e :
        db.rollback()
        add_error(e,db)
        return schemas.SessionOut(
            message=" database error occured",
            status=status.HTTP_400_BAD_REQUEST,)

@router.post("/getall_session",response_model=schemas.SessionsOut)
def get_all_sessions(page_number : int ,page_size:int ,name_filter :str =None, db: Session = Depends(get_db)   ,current_user=Depends(get_current_user([Role.vendor, Role.super_user]))):
    try:
        total_records = db.query(modelSession).count()
        total_pages = utils.div_ceil(total_records,page_size)
        user_roles = db.query(EmployeeRole).filter_by(employee_id = current_user.id).all()
        user_role_names = [role.role for role in user_roles]

        if Role.vendor in user_role_names:
            sessions_query = db.query(modelSession).filter_by(employee_id=current_user.id)

        elif Role.super_user in user_role_names:
            if name_filter:
                employee_query = db.query(Employee).filter_by(firstname = name_filter).first()
                employee_id = employee_query.id
                sessions_query = db.query(modelSession).filter_by(employee_id = employee_id)
            else:
                sessions_query = db.query(modelSession)

        sessions =sessions_query.offset((page_number-1) * page_size).limit(page_size).all()

        return schemas.SessionsOut(
            total_pages = total_pages,
            total_records = total_records,
            page_number = page_number,
            page_size = page_size,
            list = [ schemas.SessionOut(**session.__dict__) for session in sessions],
            status=status.HTTP_200_OK )
    except Exception :
        return schemas.SessionOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )


@router.get('/current_session')
def get_current_active_sessions(page_number: int, page_size:int, db: Session = Depends(get_db)):
    try:
        existing_session_query = db.query(modelSession).filter(
            modelSession.end_date.is_(None),
            modelSession.session_status == SessionStatus.open
        )

        total_records = existing_session_query.count()
        total_pages = utils.div_ceil(total_records, page_size)
        sessions = existing_session_query.offset((page_number - 1) * page_size).limit(page_size).all()

        if not sessions:
            return schemas.SessionOut(
                status=status.HTTP_404_NOT_FOUND,
                message="No active sessions found"
            )
    except Exception :
        return schemas.SessionOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )
    return schemas.SessionOut(
        total_pages = total_pages,
        total_records = total_records,
        page_number = page_number,
        page_size = page_size,
        list = [ schemas.SessionOut(**session.__dict__) for session in sessions],
        status=status.HTTP_200_OK,
        )

