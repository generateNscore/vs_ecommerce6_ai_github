from fastapi import FastAPI
from app.routers import (admin, dashboard, ai)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="E-Commerce6 with AI (admin)")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

@app.get("/")
async def home(request: Request):  # frontend webpage
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

app.include_router(admin.router) # swagger: http://localhost:8000/docs
app.include_router(dashboard.router) # frontend에서 fetch로 호출하는 api: http://localhost:8000/dashboard/summary, http://localhost:8000/dashboard/monthly_sales, http://localhost:8000/dashboard/piechart_categories, http://localhost:8000/dashboard/barchart_cities
app.include_router(ai.router) # ai agent 호출 endpoints
