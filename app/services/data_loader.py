from sqlalchemy.orm import Session
from app.services.fake_data import ECommerceWorld

def dump_to_db(data: ECommerceWorld, db: Session):
    try:
        db.add_all(data.customers)
        db.add_all(data.categories)
        db.add_all(data.products)
        db.add_all(data.orders)
        db.add_all(data.order_items)

        db.commit()
    except Exception as e:
        db.rollback()
        print('error', e)

