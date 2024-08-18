from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy.exc import SQLAlchemyError
import models, schemas

router = APIRouter(
    prefix="/companies",
    tags=['Company']
)

@router.post("/create", response_model=schemas.CompanyOut)
async def create_company(company: schemas.Company, db: Session = Depends(get_db),):
    try:
        company_to_add = models.Company(name = company.name,
                                        last_employee_number= 0)
        db.add(company_to_add)
        db.commit()
        db.refresh(company_to_add)
    except SQLAlchemyError as e:
        db.rollback()
        return schemas.CompanyOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong"
        )
    return schemas.CompanyOut(
        **company_to_add.__dict__,
        status=status.HTTP_201_CREATED,
        message="Company created successfully"
    )
