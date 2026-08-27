from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.services.data_generator import generate_fake_data
# from app.services.data_loader import dump_to_db
from app.services.analytics import analyse #, test_analyze
# from app.config import DEBUG_RESET_DB # commented 2026.08.21
# from app.services.load_data_from_db import load_from_db
from app.database import Base, engine
from app.schemas import Prms2Create

router = APIRouter(prefix="/admin", tags=["Admin"])

# @router.post("/admin/generate_data") # commented 2026.08.21
# def generate_data(db: Session = Depends(get_db)):
#
#     if DEBUG_RESET_DB:
#         world = generate_fake_data(customer_count = 567,
#                                    product_count = (5,6),
#                                    order_count = 8901,
#                                    city_count = 5)
#         db.add_all(world.customers)  # 이 둘만 추가해도 됨.
#         db.add_all(world.categories)  # 이 둘만 추가해도 됨.
#         db.commit()
#     else:
#         analyse(db)


@router.post("/admin/recreate_tables", status_code=status.HTTP_200_OK)
def recreate_tables():
    """
    Drops all existing tables and creates them fresh from the metadata.
    """
    try:
        # Drop all tables safely
        Base.metadata.drop_all(bind=engine)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        return {"status": "success", "message": "All tables dropped and recreated successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )


@router.post("/admin/generate_add_data")
def generate_add_data(prms: Prms2Create, db: Session = Depends(get_db)):
    customer_count = prms.customer_count if prms.customer_count else 5
    product_count = prms.product_count if prms.product_count else (3,4)
    order_count = prms.order_count if prms.order_count else 100
    city_count = prms.city_count if prms.city_count else 5

    world = generate_fake_data(customer_count = customer_count,
                               product_count = product_count,
                               order_count = order_count,
                               city_count = city_count)
    db.add_all(world.customers)  # 이 둘만 추가해도 됨.
    db.add_all(world.categories)  # 이 둘만 추가해도 됨.
    db.commit()
    analyse(db)
