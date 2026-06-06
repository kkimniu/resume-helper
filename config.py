import os
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = "gpt-4o-mini"

def ini_env() -> bool:
    required = ["OPENAI_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"환경변수 누락: {', '.join(missing)}")
        print("프로젝트 루트 .env파일에 해당 키를 추가합니다.")
        return False
    print("환경 변수 확인 완료")
    return True

if __name__=="__main__":
    ini_env()