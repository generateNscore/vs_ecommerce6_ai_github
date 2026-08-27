from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import QueryRequest, QueryResponse
from app.services_ai import sql_agent

router = APIRouter(prefix="/ai", tags=["AI Agent"])

@router.post("/query", response_model=QueryResponse)
def query_ai(request: QueryRequest, db: Session = Depends(get_db)):
    sql, system_prompt = sql_agent.question_to_sql(request.question)
    print(f"--------[System Prompt]: {system_prompt}") # for debugging
    print(f"--------[AI Generated SQL]: {sql}") # for debugging
 
    db_result = sql_agent.execute_sql(db, sql)
    natural_answer = sql_agent.answer_with_data(request.question, db_result)

    # Return MUST match QueryResponse field names
    return QueryResponse(
        question=request.question,
        sql=db_result["sql"],
        columns=db_result["columns"],
        rows=db_result["rows"],
        answer=natural_answer
    )

# 위 def chat_with_ai는 자연어 질의(natural language query)를 처리하고 응답을 제공하는 
# 엔드포인트를 정의합니다. 클라이언트가 POST 요청을 보내면, 
# 요청 본문에서 자연어 질의를 받아서 단순히 그 질의를 그대로 반환하는 기능을 수행합니다. 
# 실제로는 이 부분에서 AI 모델을 호출하여 질의에 대한 적절한 응답을 생성하도록 구현할 수 있습니다. 
# 현재처럼 return {'response': request.query)만 있는 경우 post 대신 get을 사용하면,
# 오류 TypeError: Failed to execute 'fetch' on 'Window': Request with GET/HEAD method cannot have body 발생
