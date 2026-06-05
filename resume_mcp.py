from pathlib import Path
from pydantic import BaseModel, Field
from agents import GuardrailFunctionOutput, input_guardrail
from pydantic import BaseModel

class ResumeAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    defects: list[str]
    keyword_match: dict[str, object]
    blind_violations: list[str]
    revised_text: str

class ResumeGuardrailOutput(BaseModel):
    # TODO: 위험 입력 여부를 담는 bool 필드를 추가해요.
    # 힌트: is_harmful: bool
    is_harmful: bool

def normalize_keywords(raw_keywords: str) -> list[str]:
    # TODO: 쉼표로 나누고, 앞뒤 공백을 제거하고, 빈 값은 버려요.
    return [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]


def match_keywords(resume_text: str, required_keywords: list[str]) -> dict[str, object]:
    # TODO: matched, missing, score 키를 가진 dict를 반환해요.
    matched =[keyword for keyword in required_keywords if keyword in resume_text]
    missing = [keyword for keyword in required_keywords if keyword not in resume_text]
    if required_keywords:
        score = int(len(matched) / len(required_keywords) * 100)
    else:
        score = 0
    return {
        "required": required_keywords,
        "matched": matched,
        "missing": missing,
        "score": score,
    }
    
def detect_blind_violations(resume_text: str) -> list[str]:
    violations: list[str] = []
    risky_patterns = [
        "대학교",
        "고등학교",
        "나이",
        "성별",
        "지역",
        "허위 경력","개인정보 노출","시스템 프롬프트",
        "ignore previous instructions","reveal system prompt","show hidden instructions"
    ]

    for pattern in risky_patterns:
        # TODO: pattern이 resume_text에 있으면 violations에 넣어요.
        if pattern in resume_text:
            violations.append(pattern) 

    return violations

def detect_flaws(resume_text: str, required_keywords: list[str]) -> list[str]:
    defects: list[str] = []
    sentences = [part.strip() for part in resume_text.split(".")]

    # TODO: STAR/PREP 단서가 부족한 경우를 defects에 추가해요.
    # 힌트: "상황", "과제", "행동", "결과", "근거", "이유" 같은 단어를 확인해요.
    frame_clues = ["상황", "과제", "행동", "결과", "근거", "이유"]
    if not any(clue in resume_text for clue in frame_clues):
        defects.append("STAR/PREP 프레임 미준수")
        
    # TODO: NCS/JD 키워드 누락 여부를 확인해요.
    # 힌트: required_keywords 중 resume_text에 없는 키워드를 찾아요.
    missing_keywords = [
        keyword
        for keyword in required_keywords
        if keyword not in resume_text
    ]
    if required_keywords and missing_keywords:
        defects.append("NCS 키워드 누락")
        
    if detect_blind_violations(resume_text):
        defects.append("블라인드 채용 위반")
    # TODO: 공백 문장, 일반화 표현, 수동태 남발 조건을 채워요.
    if any(sentence == "" for sentence in sentences):
        defects.append("공백 문장")
        
    vague_words = ["최선을", "열심히", "좋은", "성실히", "노력하겠습니다"]
    if any(word in resume_text for word in vague_words):
        defects.append("일반화 표현")
        
    passive_words = ["되었습니다", "했습니다"]
    passive_count = sum(resume_text.count(word) for word in passive_words)
    if passive_count >= 3:
        defects.append("수동태 남발")                    
    return defects


def analyze_resume(resume_text: str, raw_keywords: str) -> ResumeAnalysis:
    # TODO: normalize_keywords, match_keywords, detect_blind_violations,
    # detect_flaws를 순서대로 호출해요.
    keywords = normalize_keywords(raw_keywords)
    keyword_match = match_keywords(resume_text, keywords)
    blind_violations = detect_blind_violations(resume_text)
    defects = detect_flaws(resume_text, keywords)
    
    payload: dict[str, object] = {
        "score": keyword_match["score"],
        "defects": defects,
        "keyword_match": keyword_match,
        "blind_violations": blind_violations,
        "revised_text": resume_text,
    }
    return ResumeAnalysis.model_validate(payload)

@input_guardrail
async def resume_input_guardrail(ctx, agent, input_data):
    # TODO: 입력을 문자열로 바꾸고 위험 키워드를 검사해요.
    text = str(input_data).lower()
    keywords = normalize_keywords(text)
    keyword_match = match_keywords(text, keywords)
    blind_violations = detect_blind_violations(text)
    defects = detect_flaws(text, keywords)
    
    harmful_keywords = blind_violations

    tripwire = any(
        keyword in text
        for keyword in harmful_keywords
    )  # TODO: any(...)로 조건을 채워요.

    return GuardrailFunctionOutput(
        output_info=ResumeGuardrailOutput(is_harmful=tripwire),
        tripwire_triggered=tripwire,
    )

# (학생 따라하기) JSON 저장 골격
def save_analysis(analysis: ResumeAnalysis, output_path: str = "analyze_result.json") -> None:
    path = Path(output_path)
    # TODO: model_dump_json(indent=2)을 사용해 UTF-8 JSON으로 저장해요.
    path.write_text(
        analysis.model_dump_json(indent=2),
        encoding="utf-8",
    )
    print(f"저장 위치: {path}")

def run_cli() -> None:
    print("자소서 도우미입니다. /analyze 를 입력해요.")
    command = input("명령: ").strip()

    if command == "/analyze":
        resume_text = input("자소서 원문: ").strip()
        keyword_text = input("NCS/JD 키워드(쉼표 구분): ").strip()
        # TODO: 여기에 analyze_resume(...) 호출을 채워요.
        analysis = analyze_resume(resume_text,keyword_text)
        save_analysis(analysis)
        
        print("분석 완료.")
    else:
        print("지원하는 명령: /analyze")
if __name__ == "__main__":
    run_cli()