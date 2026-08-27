from pydantic import BaseModel
from typing import List, Any

# 데이터를 생성할 때 필요한 내용들을 담은 변수에 대한 클라이언트가 보내야 하는 형태
class Prms2Create(BaseModel):
    customer_count: int
    product_count: tuple[int, int] # categories, products in each category
    order_count: int
    city_count: int

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    columns: List[str]
    rows: List[List[Any]] # will contain str/float after conversion
    answer: str

    class Config:
        json_encoders = {
            # just in case Decimal leaks through
            float: lambda v: float(v)
        }