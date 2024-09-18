from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session
from database import get_db
from enums import Role
import models
import schemas
from security import get_current_user
from sqlalchemy.exc import SQLAlchemyError
from error import add_error, get_error_message , error_keys
import utils

router=APIRouter(
    prefix="/pricelist",
    tags=["pricelist"]
)

@router.post("/add pricelist" , response_model=schemas.pricelistOut)
def add_pricelist (pricelist : schemas.PricelistIn  ,current_user=Depends(get_current_user([Role.admin, Role.super_user])),db: Session = Depends(get_db)):
    try:
        pricelist_input = models.Pricelist(name = pricelist.name,
                                description = pricelist.description,
        )
        db.add(pricelist_input)
        db.commit()
        return schemas.pricelistOut(
            message=" added",
            status=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        add_error(e,db)
        return schemas.pricelistOut(
            message= get_error_message(str(e.__dict__['orig']), error_keys),
            status=status.HTTP_400_BAD_REQUEST,
        )
@router.post("/add-pricelistline", response_model=schemas.pricelistLineOut)
def add_pricelistline(
    pricelistline: schemas.PricelistLine,
    current_user=Depends(get_current_user([Role.admin, Role.super_user])),
    db: Session = Depends(get_db)
):
    try:
        product_query = db.query(models.Product).filter_by(name=pricelistline.product_name).first()
        if not product_query:
            return schemas.pricelistLineOut(
                message="Product does not exist.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        pricelist_query = db.query(models.Pricelist).filter_by(name=pricelistline.pricelist_name).first()
        if not pricelist_query:
            return schemas.pricelistLineOut(
                message="Pricelist name does not exist.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        pricelistline_input = models.PricelistLine(
            new_price=pricelistline.new_price,
            min_quantity=pricelistline.min_quantity,
            start_date=pricelistline.start_date,
            end_date=pricelistline.end_date,
            product_id=product_query.id,
            pricelist_id=pricelist_query.id
        )
        db.add(pricelistline_input)
        db.commit()

        return schemas.pricelistLineOut(
            message="Pricelist line added successfully.",
            status=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        return schemas.pricelistLineOut(
            message=get_error_message(str(e.__dict__.get('orig', '')), error_keys),
            status=status.HTTP_400_BAD_REQUEST,
        )

@router.post("/getallpricelists",response_model=schemas.pricelistsOut)
def get_all_pricelists(page_number : int ,page_size:int, db: Session = Depends(get_db) ):
    try:
        pricelist =  db.query(models.Pricelist)
        total_records = db.query(models.Pricelist).count()
        total_pages = utils.div_ceil(total_records,page_size)
        pricelists = pricelist.offset((page_number-1) * page_size).limit(page_size).all()

        return schemas.pricelistsOut(
            total_records = total_records,
            total_pages = total_pages,
            page_number = page_number,
            page_size = page_size,
            list = [schemas.pricelistOut(**pricelist.__dict__) for pricelist in pricelists],
            status=status.HTTP_200_OK, )
    except Exception :
        return schemas.pricelistsOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )

@router.post("/getallpricelistlines",response_model=schemas.pricelistlinesOut)
def get_all_pricelist_lines(page_number : int ,page_size:int, db: Session = Depends(get_db) ):
    try:
        pricelistline =  db.query(models.PricelistLine)
        total_records = db.query(models.PricelistLine).count()
        total_pages = utils.div_ceil(total_records,page_size)
        pricelistlines = pricelistline.offset((page_number-1) * page_size).limit(page_size).all()

        return schemas.pricelistlinesOut(
            total_records = total_records,
            total_pages = total_pages,
            page_number = page_number,
            page_size = page_size,
            list = [schemas.pricelistLineOut(**pricelistline.__dict__) for pricelistline in pricelistlines],
            status=status.HTTP_200_OK, )
    except Exception :
        return schemas.pricelistlinesOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )

