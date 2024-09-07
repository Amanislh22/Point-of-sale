from datetime import datetime
from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session
from database import get_db
from enums import Role
from enums.SessionStatus import SessionStatus
from models.customer import Customer
from models.employee import Employee
from models.order import Order
from models.order_line import OrderLine
from models.product import Product
from models.session import Session as modelSession
import schemas
from security import get_current_user
import utils

router=APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("/add order" , response_model=schemas.orderLineOut)
def add_order(order : schemas.OrderIn  ,current_user=Depends(get_current_user([Role.vendor, Role.super_user])),db: Session = Depends(get_db)):
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
        new_order = Order(number = order.number,
                    customer_id = customer_id,
                    session_id=session_id,
                    created_on = datetime.utcnow(),
                    total_price = total_price)

        db.add(new_order)
        db.flush()


        order_lines_to_add=[]
        for product in order.products:
                new_order_line = OrderLine(order_id = new_order.id,
                                product_id =product_record.id,
                                unit_price =product_record.unit_price,
                                quantity = quantity,
                                total_price = quantity*product_record.unit_price)

                order_lines_to_add.append(new_order_line)

        db.add_all(order_lines_to_add)
        db.commit()
    except Exception :
        db.rollback()
        return schemas.orderLineOut(
            message= " db error occured",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
