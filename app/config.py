from dotenv import load_dotenv
import os

load_dotenv(override=True)  # .env 파일의 환경 변수를 강제로 로드합니다.

DATABASE_URL = os.getenv("DATABASE_URL")
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
# DEBUG_RESET_DB = False # True면 db에 있는 모든 자료를 삭제하고 초기화한다. # commented 2026.08.21

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")  # Ollama API base URL