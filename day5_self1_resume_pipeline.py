import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

MODEL_OPENAI = os.getenv("MODEL_OPENAI", "gpt-5.4-nano")


def check_resume_ai_filter(resume_text: str, check_items: list[str]) -> str:
    """선택한 검증 항목을 기준으로 자소서를 점검해요."""
    system_prompt = (
        "당신은 AI 1차 필터 역할을 하는 자소서 점검 도우미입니다.\n"
        "검증 항목을 기준으로 자소서를 점검하고, 개선 권고를 1개 이상 제시하세요.\n"
        f"검증 항목: {', '.join(check_items)}"
    )
    # TODO: client.chat.completions.create 호출 코드를 채워요.
    response =client.chat.completions.create(
        # TODO: model에는 MODEL_OPENAI를 사용해요.
        model= MODEL_OPENAI,
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
    "허위 경력",
    "개인정보 노출",
]


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


if __name__ == "__main__":
    sample_items = ["STAR 구조 충족 여부", "정량 근거 포함 여부", "NCS 직무 키워드 밀도"]
    sample_text = """"
        프로젝트에서 REST API 개발을 담당했습니다.
        사용자 요청 처리 속도를 개선했습니다.
    """
    result = check_resume_ai_filter(sample_text, sample_items)
    print(result)
