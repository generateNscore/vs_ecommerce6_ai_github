from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from app.services_ai.schema_generator import DB_SCHEMA
from app.services_ai.llm_client import call_llm

# SYSTEM_PROMPT = f"""
# You are a PostgreSQL expert. Convert natural language to SQL.

# RULES:
# 1. Output ONLY a single SELECT query. No explanation.
# 2. FORBIDDEN: INSERT, UPDATE, DELETE, DROP, ALTER.
# 3. ONLY use tables/columns from schema below.
# 4. Use ILIKE for Korean name search.
# 5. For time: 지난달 = WHERE order_date >= DATE_TRUNC('month', NOW() - INTERVAL '1 month') AND order_date < DATE_TRUNC('month', NOW())

# Schema (auto-generated from models.py):
# {DB_SCHEMA}

# Few-shot for THIS schema:
# Q: 지난달 매출 1위 상품이 뭐야?
# A: SELECT p.name, SUM(oi.quantity * oi.unit_price) as revenue FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON o.id = oi.order_id WHERE o.order_date >= DATE_TRUNC('month', NOW() - INTERVAL '1 month') AND o.order_date < DATE_TRUNC('month', NOW()) GROUP BY p.name ORDER BY revenue DESC LIMIT 1;

# Q: 서울 고객 수?
# A: SELECT COUNT(*) FROM customers WHERE city = '서울';
# """


SYSTEM_PROMPT = f"""
당신은 PostgreSQL 전문가인 SQL 생성 에이전트입니다.
사용자의 한국어 질문을 분석하여 올바른 PostgreSQL 쿼리만 생성하세요.

[규칙]
1. 사족이나 설명(예: "네, 요청하신 쿼리입니다")은 절대 출력하지 마세요.
2. 오직 [SQL]과 [/SQL] 태그 사이에만 쿼리를 작성하세요.
3. 데이터베이스 스키마에 존재하지 않는 테이블이나 컬럼은 절대 사용하지 마세요.
4. 사용 금지: INSERT, UPDATE, DELETE, DROP, ALTER.

[데이터베이스 스키마 (DDL)]
{DB_SCHEMA}

[참고 예시 (Few-Shot)]
Q: 서울에서 mobile 종류(category)로 판매된 상품은 몇 개야?
A: SELECT COUNT(oi.id) FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id JOIN categories cat ON cat.id = p.category_id WHERE c.city = '서울' AND cat.name = 'mobile';

Q: 서울 고객 수?
A: SELECT COUNT(*) FROM customers c WHERE c.city = '서울';
"""






def question_to_sql(question: str) -> str:
    return call_llm(SYSTEM_PROMPT, question), SYSTEM_PROMPT

def convert_value(v): # 아래 execute_sql()의 끝 부분에서 사용
    # Fix for JSON serialization
    if isinstance(v, Decimal):
        return float(v)
    return v

def execute_sql(db: Session, sql: str):
    if not sql.lower().strip().startswith("select"):
        raise ValueError("Only SELECT allowed")

    result = db.execute(text(sql))
    rows = result.fetchall()
    columns = list(result.keys())

    # Convert Decimal and datetime to JSON-safe types
    safe_rows = [[convert_value(col) for col in row] for row in rows]

    return {"sql": sql, "columns": columns, "rows": safe_rows}

def answer_with_data(question: str, sql_result: dict) -> str:
    # Second LLM call to make natural Korean answer
    prompt = f"Question: {question}\nSQL Result: {sql_result['rows']}\n이 결과를 보고 한국어로 친절하게 답변해줘. 숫자가 있으면 포맷팅해줘."
    return call_llm("You are a helpful data analyst.", prompt)

