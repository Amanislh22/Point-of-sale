import uuid
from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
import models, schemas
from sqlalchemy import func
from error import error_keys, add_error, get_error_message
import utils

router = APIRouter(
    prefix="/program",
    tags=['Program']
)

@router.post('/',response_model=schemas.ProgramOut)
def create_program(program: schemas.ProgramIn, count_item :int, db: Session = Depends(get_db)):
    program_items =[]
    try:
        product_buy_id = program.product_buy_id if program.product_buy_id != 0 else None
        product_get_id = program.product_get_id if program.product_get_id != 0 else None
        program_to_add = models.Program(
            name=program.name,
            description=program.description,
            program_type=program.program_type,
            discount=program.discount,
            start_date=program.start_date,
            end_date=program.end_date,
            product_buy_id=product_buy_id,
            product_get_id=product_get_id,
            count = program.count,
        )
        db.add(program_to_add)
        db.flush()
        program_items = [
            models.ProgramItem(
            code=uuid.uuid4(),
            program_id=program_to_add.id,
            )
        for _ in range(count_item)
        ]

        db.add_all(program_items)
        db.commit()
        return schemas.ProgramOut(
        status=status.HTTP_201_CREATED,
        message="Program and program_items created successfully",
    )
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e, db)
        return schemas.ProgramOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(str(e.__dict__.get('orig', '')), error_keys),)

@router.get('/')
def get_programs(page_number : int, page_size:int, db: Session = Depends(get_db)):
    programs_query = db.query(models.Program)
    total_records = programs_query.count()
    total_pages = utils.div_ceil(total_records,page_size)
    return schemas.ProgramsOut(
        total_records = total_records,
        total_pages = total_pages,
        page_number = page_number,
        page_size = page_size,
        list=[
            schemas.ProgramOut(**program.__dict__)
            for program in programs_query.all()
        ],
        status=status.HTTP_200_OK,
        message="Programs retrieved successfully",
    )

@router.get('/getprogramitems')
def get_program_items(page_number : int, page_size:int, db: Session = Depends(get_db)):
    programs_query = db.query(models.ProgramItem)
    total_records = programs_query.count()
    total_pages = utils.div_ceil(total_records,page_size)
    return schemas.ProgramItemsOut(
        total_records = total_records,
        total_pages = total_pages,
        page_number = page_number,
        page_size = page_size,
        list=[
            schemas.ProgramItemOut(**program_item.__dict__)
            for program_item in programs_query.all()
        ],
        status=status.HTTP_200_OK,
        message="Program items  retrieved successfully",
    )


