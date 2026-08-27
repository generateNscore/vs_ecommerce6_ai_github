from fastapi import APIRouter, Depends
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.services.analytics import dashboard_summary, monthly_sales, piechart_categories, barchart_cities

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_summary(city: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    return dashboard_summary(db, city, category)


@router.get("/monthly_sales")
def get_monthly_sales(city: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    return monthly_sales(db, city)

@router.get("/piechart_categories")
def get_piechart(city: str | None = None, db: Session = Depends(get_db)):
    return piechart_categories(db, city)

@router.get("/barchart_cities")
def get_barchart(category: str | None = None, db: Session = Depends(get_db)):
    return barchart_cities(db, category)
