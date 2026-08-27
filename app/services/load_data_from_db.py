from sqlalchemy.orm import Session
from app.models import Customer, Category, Product, Order, Order_item
from app.services.fake_data import ECommerceWorld

def load_from_db(db: Session):
    customers = db.query(Customer).all()
    categories = db.query(Category).all()
    products = db.query(Product).all()
    # orders = db.query(Order).order_by(Order.id).all()
    orders = db.query(Order).all()
    order_items = db.query(Order_item).all()


    return ECommerceWorld(
        customers = customers,
        categories = categories,
        products = products,
        orders = orders,
        order_items = order_items,
    )
