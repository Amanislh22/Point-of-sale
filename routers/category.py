from fastapi import APIRouter
import models
import schemas
from fastapi import  Depends , status
from database import get_db
from sqlalchemy.orm import Session
import utils

router=APIRouter(
    prefix="/category",
    tags=["categories"]
)

@router.post("/add" , response_model=schemas.categoryOut)
def add_category(category : schemas.CategoryIn ,  db: Session = Depends(get_db)):
    try:
        existing_category = db.query(models.Category).filter_by(id=category.id).first()

        if existing_category :
            return schemas.categoryOut(
                message= "category name already exist",
                status=status.HTTP_400_BAD_REQUEST,
            )
        category_input = models.Category(name = category.name,
                                icon_name = category.icon_name,
                                description = category.description,
        )
        db.add(category_input)
        db.commit()
    except Exception :
        db.rollback()
        return schemas.categoryOut(
            message="Database error occured",
            status=status.HTTP_400_BAD_REQUEST,
        )
    return schemas.categoryOut(
        message=" Category added sucessfly",
        status=status.HTTP_201_CREATED,
    )

@router.post("/edit" , response_model=schemas.categoryOut)
def edit_category(category : schemas.CategoryIn,  db: Session = Depends(get_db)):
    try:
        existing_category = db.query(models.Category).filter_by(id=category.id).first()

        if not existing_category :
            return schemas.categoryOut(
                message= "category not found",
                status=status.HTTP_400_BAD_REQUEST,
            )
        existing_category.name = category.name
        existing_category.icon_name = category.icon_name
        existing_category.description = category.description
        db.commit()

    except Exception  :
        db.rollback()
        return schemas.categoryOut(
            message="Database error occured",
            status=status.HTTP_400_BAD_REQUEST,
        )
    return schemas.categoryOut(
        message=" Category edited sucessfly",
        status=status.HTTP_201_CREATED,
    )

@router.post("/delete" , response_model=schemas.categoryOut)
def delete_category(id : int,  db: Session = Depends(get_db)):
    try:
        existing_category = db.query(models.Category).filter_by(id=id).first()

        if not existing_category :
            return schemas.categoryOut(
                message= "category not found",
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = db.query(models.Product).filter_by(category_id=id).first()
        if product :
            return schemas.categoryOut(
                message=" We can only delete categories which have no products",
                status=status.HTTP_400_BAD_REQUEST,)

        db.delete(existing_category)
        db.commit()

    except Exception as e :
        db.rollback()
        return schemas.categoryOut(
            message="Database error occured",
            status=status.HTTP_400_BAD_REQUEST,
        )
    return schemas.categoryOut(
        message=" Category deleted successfly",
        status=status.HTTP_201_CREATED,
    )

@router.post("/getall",response_model=schemas.categoriesOut)
def get_all_categories(page_number : int ,page_size:int ,name_filter :str =None, db: Session = Depends(get_db) ):
    try:
        query =  db.query(models.Category)
        if name_filter:
           query = query.filter_by(name=name_filter)

        total_records = db.query(models.Category).count()
        total_pages = utils.div_ceil(total_records,page_size)
        categories = query.offset((page_number-1) * page_size).limit(page_size).all()

        return schemas.categoriesOut(
            total_records = total_records,
            total_pages = total_pages,
            page_number = page_number,
            page_size = page_size,
            list = [schemas.categoryOut(**category.__dict__) for category in categories],
            status=status.HTTP_200_OK, )
    except Exception :
        return schemas.categoriesOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wrong",
        )
