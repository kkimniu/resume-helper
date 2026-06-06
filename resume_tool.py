# (학생 따라하기) day3_self1_resume_tool.py
from pathlib import Path

from agents import GuardrailFunctionOutput, input_guardrail
from openai import OpenAI
from pydantic import BaseModel, Field

from config import MODEL_NAME

class ResumeAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    defects: list[str]
    keyword_match: dict[str, object]
    blind_violations: list[str]
    revised_text: str

class ResumeGuardrailOutput(BaseModel):
    is_harmful: bool


BLIND_RISK_WORDS = [
    # TODO: 블라인드 채용에서 조심할 표현 후보를 채워요.
    "대학교",
    "고등학교",
    "나이",
    "성별",
    "지역",
    "가족",
    "사진",
    "주소",
    "전화번호",
]

DANGEROUS_PATTERNS = [
    "시스템 프롬프트",
    "이전 지시 무시",
    "지시 무시",
    "허위 경력",
    "ignore previous instructions",
    "reveal system prompt",
    "show hidden instructions",
]

CHECK_ITEMS = [
    "STAR 구조 충족 여부",
    "정량 근거 포함 여부",
    "NCS 직무 키워드 밀도",
]

def check_resume_ai_filter(resume_text: str, check_items: list[str]) -> str:
    """선택한 검증 항목을 기준으로 자소서를 점검해요."""
    client = OpenAI()
    system_prompt = (
        "당신은 AI 1차 필터 역할을 하는 자소서 점검 도우미입니다.\n"
        "검증 항목을 기준으로 자소서를 점검하고, 개선 권고를 1개 이상 제시하세요.\n"
        f"검증 항목: {', '.join(check_items)}"
    )
    # TODO: client.chat.completions.create 호출 코드를 채워요.
    response = client.chat.completions.create(
        # TODO: model에는 MODEL_OPENAI를 사용해요.
        model= MODEL_NAME,
        # TODO: messages에는 developer 또는 system 역할 지시와 user 자소서 본문을 넣어요.
        messages=[
            {
                "role": "developer",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": resume_text,
            }, 
        ],
        max_completion_tokens=800,
        # TODO: GPT-5 계열은 max_completion_tokens를 사용해요.
    )
    return response.choices[0].message.content # TODO: 응답 텍스트만 반환해요.


def check_blind_risks(resume_text: str) -> list[str]:
    """블라인드 채용 위험 표현 후보를 찾아요."""
    found = []
    for word in BLIND_RISK_WORDS:
        # TODO: resume_text 안에 word가 있으면 found에 추가해요.
        if word in resume_text:
            found.append(word)
    return found

def format_blind_report(found: list[str]) -> str:
    """위험 표현 후보를 사람이 읽기 쉬운 문장으로 바꿔요."""
    if not found:
        return "블라인드 채용 위험 표현 후보가 발견되지 않았어요."
    # TODO: 발견된 표현을 줄바꿈 목록으로 정리해요.
    return "블라인드 채용 위험 표현 후보:\n" + "\n".join(f"- {word}" for word in found)

def normalize_keywords(raw_keywords: str) -> list[str]:
    return [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]

def match_keywords(resume_text: str, required_keywords: list[str]) -> dict[str, object]:
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
    return check_blind_risks(resume_text)

def detect_prompt_injection(resume_text: str) -> list[str]:
    violations: list[str] = []

    lower_text = resume_text.lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in lower_text:
            violations.append(pattern)

    return violations

def detect_flaws(resume_text: str, required_keywords: list[str]) -> list[str]:
    defects: list[str] = []
    frame_clues = ["상황", "과제", "행동", "결과", "근거", "이유"]
    if not any(clue in resume_text for clue in frame_clues):
        defects.append("STAR/PREP 프레임 미준수")

    missing_keywords = [
        keyword
        for keyword in required_keywords
        if keyword not in resume_text
    ]

    if required_keywords and missing_keywords:
        defects.append("NCS 키워드 누락")

    if detect_blind_violations(resume_text):
        defects.append("블라인드 채용 위반")
    vague_words = ["최선을", "열심히", "좋은", "성실히", "노력하겠습니다"]

    if any(word in resume_text for word in vague_words):
        defects.append("일반화 표현")

    return defects

def analyze_resume(resume_text: str, raw_keywords: str) -> ResumeAnalysis:
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
    text = str(input_data)
    prompt_injections = detect_prompt_injection(text)
    tripwire = bool(prompt_injections)
    
    return GuardrailFunctionOutput(
        output_info=ResumeGuardrailOutput(
            is_harmful=tripwire,
        ),
        tripwire_triggered=tripwire,
    )

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
        analysis = analyze_resume(resume_text,keyword_text)
        save_analysis(analysis)
        
        print("분석 완료.")
    else:
        print("지원하는 명령: /analyze")
if __name__ == "__main__":
    run_cli()