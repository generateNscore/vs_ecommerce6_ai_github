from openai import OpenAI
from app.config import OLLAMA_BASE_URL


# For Ollama
client = OpenAI(
    # base_url="http://ollama:11434/v1", # or "http://localhost:11434/v1" if running locally
    base_url=OLLAMA_BASE_URL,  # Use the value from .env
    api_key="ollama"
)

MODEL_NAME = "qwen2.5-coder:7b"  # Ollama 모델 이름, .env에서 가져올 수도 있음

# For laptop with 8GB RAM
# qwen2.5:7b           4.7GB ∼65% ❌ Not for SQL
# qwen2.5-coder:7b     4.7GB ∼85% ✅ Use this for SQL step
# sqlcoder:7b          4.5GB ∼90% but English only ✅ Best SQL, but need translation
# qwen2.5-coder:14b Q4 8.5GB ∼92% Too big for you

def call_llm(system_prompt: str, user_prompt: str) -> str:
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    content = res.choices[0].message.content.strip()
    # remove ```sql ``` if model adds it
    return content.replace("```sql","").replace("```","").strip()