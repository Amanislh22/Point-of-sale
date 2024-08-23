from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from enums import Role, codeStatus
from enums.SessionStatus import SessionStatus
from error import error_keys, add_error, get_error_message
import models
from models.customer import Customer
from models.employee import Employee
from models.order import Order
from models.order_line import OrderLine
from models.product import Product
from models.session import Session as modelSession
import schemas
from security import get_current_user
import utils
from sqlalchemy.exc import SQLAlchemyError

router=APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("/add order" , response_model=schemas.orderLineOut)
def add_order(order : schemas.OrderIn  ,current_user=Depends(get_current_user([Role.vendor, Role.super_user, Role.admin])),db: Session = Depends(get_db)):
    try:
        session_record = db.query(modelSession).filter_by(employee_id=current_user.id,session_status= SessionStatus.open).first()
        if not session_record:
            return schemas.orderLineOut(
                message=f"there is  no open session for the user {current_user.firstname}",
                status=status.HTTP_404_NOT_FOUND,
                )
        session_id = session_record.id
        total_price = 0
        products_out = []
        products = order.products
        existing_products = db.query(Product).filter(Product.id.in_([product.id for product in products])).all()

        product_dict = {p.id: p for p in existing_products}

        for product in products:
                name = product.name
                quantity = product.quantity
                product_record = product_dict.get(product.id)
                if not product_record:
                    return schemas.orderLineOut(
                        message=f"Product {name} not found",
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if product_record.quantity - quantity >= 0:
                    total_price += product_record.unit_price * quantity
                    product_record.quantity = product_record.quantity - quantity
                    db.flush()
                    products_out.append({
                        "name": name,
                        "quantity": quantity,
                        "unit_price": product_record.unit_price,
                        "id" : product_record.id,
                    })
                else :
                    return schemas.orderLineOut(
                        message = " insufficient quantity ",
                        status = status.HTTP_404_NOT_FOUND
                    )

        customer_record = db.query(Customer).filter_by(email=order.customer_email).first()

        if customer_record:
            customer_id = customer_record.id
        else :
            customer_id =None

        if order.pricelist_name:
            pricelist_query = db.query(models.Pricelist).filter_by(name=order.pricelist_name).first()
            if not pricelist_query:
                return schemas.orderLineOut(
                message= "price list name not exist",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
            product_names = [product.name for product in order.products]
            product_ids = db.query(models.Product.id).filter(models.Product.name.in_(product_names)).all()
            product_ids = [product_id[0] for product_id in product_ids]
            pricelist_lines_query = db.query(models.PricelistLine).filter_by(pricelist_id=pricelist_query.id).filter(
                models.PricelistLine.product_id.in_(product_ids)
            ).all()

            for product, product_id in zip(order.products, product_ids):
                pricelist_line = next((line for line in pricelist_lines_query if line.product_id == product_id), None)
                if pricelist_line:
                    if product.quantity >= pricelist_line.min_quantity:
                        original_unit_price = product_dict[product.id].unit_price
                        total_price -= original_unit_price * product.quantity
                        total_price += pricelist_line.new_price * product.quantity

        if order.discount_code:
            program_item_query = db.query(models.ProgramItem).filter_by(code = order.discount_code).first()
            if program_item_query.code_status != codeStatus.active:
                return schemas.orderLineOut(
                    message ="discount code inactive",
                    status=status.HTTP_200_OK,
                    products= products_out,
                    total_price = total_price,
                    )

            program_query = db.query(models.Program).filter_by(id = program_item_query.program_id).first()
            if program_query.discount:
                discount_percent = program_query.discount
                total_price= total_price - (discount_percent/100)*total_price
            else :
                product_to_buy_query = db.query(Product).filter_by(id=program_query.product_buy_id).first()
                if not product_to_buy_query:
                    return schemas.orderLineOut(
                        message="Product to buy not found",
                        status=status.HTTP_400_BAD_REQUEST,
                        products=products_out,
                        total_price=total_price,
                    )

                product_to_get_query = db.query(Product).filter_by(id=program_query.product_get_id).first()
                if not product_to_get_query:
                    return schemas.orderLineOut(
                    message="Product to get not found",
                    status=status.HTTP_400_BAD_REQUEST,
                    products=products_out,
                    total_price=total_price,
    )

                total_quantity_x = 0

                for p in products:
                    if p.id == product_to_buy_query.id:
                        total_quantity_x += p.quantity

                if program_query.count and program_query.count > 0:
                    applicable_promotion_count = total_quantity_x // program_query.count
                    product_to_get_query.quantity -= applicable_promotion_count
                    products_out.append({
                        "name": product_to_get_query.name,
                        "quantity": applicable_promotion_count,
                        "unit_price": product_to_get_query.unit_price,
                        "id" : product_to_get_query.id,
                    })

            program_item_query.code_status = codeStatus.inactive

        new_order = Order(number = order.number,
                    customer_id = customer_id,
                    session_id=session_id,
                    created_on = datetime.utcnow(),
                    total_price = total_price)

        db.add(new_order)
        db.flush()


        order_lines_to_add=[]
        for product in order.products:
                name = product.name
                quantity = product.quantity
                product_record = product_dict.get(product.id)
                new_order_line = OrderLine(order_id = new_order.id,
                                product_id =product_record.id,
                                unit_price =product_record.unit_price,
                                quantity = quantity,
                                total_price = quantity*product_record.unit_price)

                order_lines_to_add.append(new_order_line)

        db.add_all(order_lines_to_add)
        db.commit()
    except SQLAlchemyError as e :
        db.rollback()
        return schemas.orderLineOut(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=get_error_message(str(e.__dict__.get('orig', '')), error_keys),
            )


    return schemas.orderLineOut(
        message =" order done",
        status=status.HTTP_200_OK,
        products= products_out,
        total_price = total_price,
    )

@router.post("/getallorder" , response_model=schemas.ordersOut)
def get_all_order(page_number : int ,page_size:int , db: Session = Depends(get_db)):

    total_records = db.query(Order).count()
    total_pages = utils.div_ceil(total_records,page_size)
    order_query =  db.query(Order)
    orders = order_query.offset((page_number-1) * page_size).limit(page_size).all()

    orders_out = []

    for order in orders:
        orders_line = order.order_lines
        order_lines_out = []
        for order_line in orders_line:
            product_query = db.query(Product).filter_by(id=order_line.product_id).first()
            products = [
                {"name": product_query.name,
                "quantity": order_line.quantity,
                "unit_price": order_line.unit_price,
                "id" : product_query.id,}
            ]

            order_line_out = schemas.orderLineOut(
                products=products,
            )
            order_lines_out.append(order_line_out)

        session_query=db.query(modelSession).filter_by(id=order.session_id).first()
        employee_query = db.query(Employee).filter_by(id = session_query.employee_id).first()

        customer_query = db.query(Customer).filter_by(id=order.customer_id).first()

        order_out = schemas.orderOut(
            session_id = order.session_id,
            date = order.created_on,
            receipt_number = order.number,
            employee = employee_query.firstname,
            customer = customer_query.name if customer_query else "Unknown",
            total = order.total_price,
            lines = order_lines_out,
        )
        orders_out.append(order_out)

    return schemas.ordersOut(
        total_records = total_records,
        total_pages = total_pages,
        page_number = page_number,
        page_size = page_size,
        list = orders_out,
        status=status.HTTP_200_OK, )

@router.post("/get_order_lines" , response_model=schemas.orderlinesOut)
def get_order_lines(page_number : int ,page_size:int ,order_id : int, db: Session = Depends(get_db)):

    total_records = db.query(OrderLine).count()
    total_pages = utils.div_ceil(total_records,page_size)
    order =  db.query(OrderLine).filter_by(order_id = order_id)
    orders_line = order.offset((page_number-1) * page_size).limit(page_size).all()
    total_price = orders_line[0].total_price

    order_lines_out = []
    for order_line in orders_line:
        product_query = db.query(Product).filter_by(id=order_line.product_id).first()
        products = [
            {"name": product_query.name,
             "quantity": order_line.quantity,
             "unit_price": order_line.unit_price,
             "id" : product_query.id}
        ]

        order_line_out = schemas.orderLineOut(
            products=products,
        )
        order_lines_out.append(order_line_out)

    return schemas.orderlinesOut(
        total_records = total_records,
        total_pages = total_pages,
        page_number = page_number,
        page_size = page_size,
        list = order_lines_out,
        total_price=total_price,
        status=status.HTTP_200_OK, )
