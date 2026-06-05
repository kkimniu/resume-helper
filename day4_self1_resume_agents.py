import os
from dotenv import load_dotenv
from agents import Agent
from agents import Runner
from agents import handoff
from agents import GuardrailFunctionOutput, input_guardrail
from pydantic import BaseModel
import asyncio

# TODO: Agents SDK에서 필요한 Agent와 Runner를 임포트해요.
# 힌트: from agents import Agent, Runner
MODEL_NAME = "gpt-4o-mini"
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(".env에 OPENAI_API_KEY를 먼저 넣어 주세요.")

def check_env() -> None:
    # TODO: OPENAI_API_KEY가 있는지만 확인해요.
    # 주의: 키 원문을 print하지 않아요.
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OPENAI_API_KEY 로딩 확인")
    else:
        print("OPENAI_API_KEY를 .env에 먼저 넣어주세요")

revise_agent = Agent(
    name="자소서_첨삭_Specialist",
    handoff_description=(
        "STAR, PREP, CAR 기준으로 자기소개서 문장을 개선하고 첨삭할 때 사용하는 전문가입니다."
    ),
    instructions="""
        당신은 자기소개서 첨삭 전문가입니다.

        첨삭 기준:
        - STAR, PREP, CAR 구조를 활용하여 문장을 개선한다.
        - 자기소개서의 6대 결함 패턴을 점검한다.
        - 한 번에 완성본을 작성하지 않고 개선 제안을 우선 제공한다.
        - 경험, 성과, 역량이 구체적으로 드러나도록 수정 방향을 제안한다.
        - 허위 경력, 허위 성과, 존재하지 않는 경험은 생성하지 않는다.

        출력 형식:
        [문제점]
        - 발견된 결함 및 개선이 필요한 부분

        [개선 제안]
        - 수정 방향 및 예시 문장

        [첨삭 이유]
        - 왜 수정이 필요한지 설명
    """,
    model=MODEL_NAME,
)

analyze_agent = Agent(
    name="ResumeAnalyzeAgent",
    # TODO: Triage가 이 Agent를 고를 때 참고할 설명을 채워요.
    # 힌트: 자소서 분석, ResumeAnalysis 5필드, 6대 결함 탐지 요청
    handoff_description="자소서 분석, ResumeAnalysis 5필드, 6대 결함 탐지 요청",
    instructions="""
    당신은 신입 개발자 면접 질문을 설계하는 기술 면접관입니다.

    분석 기준:
    - 성장: 성장 과정이 구체적인 경험과 함께 설명되었는가
    - 동기: 지원 동기가 직무와 연결되어 있는가
    - 포부: 입사 후 목표와 계획이 명확한가
    - 경험: 직무 관련 경험과 역할이 드러나는가
    - 성공실패: 성공 또는 실패 경험에서 배운 점이 있는가

    결함 점검:
    - 추상적 표현: 구체적 근거 없이 추상적인 표현만 사용했는가
    - 수치 부재: 성과를 나타내는 수치가 부족한가
    - 복붙 흔적: 다른 항목과 유사한 표현이 반복되는가
    - 직무 불일치: 직무와 관련 없는 내용이 많은가
    - NCS 미반영: 입력된 직무 키워드가 반영되지 않았는가
    - 블라인드 위반: 학교, 나이, 성별, 지역 정보가 포함되었는가

    출력은 짧은 분석 요약과 결함 태그 중심으로 작성해요.
    """,
)
final_agent = Agent(
    name="자소서_최종본_Specialist",
    handoff_description=(
        "첨삭 결과를 반영하여 제출용 자기소개서 최종 문단을 작성하는 전문가입니다."
    ),
    instructions="""
        당신은 자기소개서 최종본 작성 전문가입니다.

        작성 기준:
        - 첨삭 결과를 반영하여 자연스럽고 완성도 높은 자기소개서를 작성한다.
        - NCS 직무 역량과 지원 직무 연관성을 강조한다.
        - 블라인드 채용 기준을 준수한다.
        - 과장된 경력이나 사실과 다른 내용은 작성하지 않는다.
        - 이름, 나이, 성별, 출신지역, 가족관계 등 개인정보는 포함하지 않는다.

        출력 형식:
        [최종 문단]
        - 제출 가능한 자기소개서 최종본

        [수정 이유]
        - 어떤 부분을 수정했는지 간단히 설명
    """,
    model=MODEL_NAME,
)

triage_agent = Agent(
    name="ResumeTriageAgent",
    instructions="""
    당신은 자소서 도우미의 접수 담당입니다.

    규칙:
    - 사용자가 자소서 분석, ResumeAnalysis, 결함 탐지를 요청하면 분석 Agent로 넘겨요.
    - 오늘 범위 밖의 첨삭, 최종본, Guardrails 요청은 다음 시간에 다룬다고 짧게 안내해요.
    - 날씨, 잡담, 일반 검색처럼 자소서와 관련 없는 요청은 범위 밖이라고 안내해요.
    - 직접 긴 분석을 작성하지 말고 적합한 Specialist를 선택해요.
    """,
    handoffs=[
        # TODO: 분석 Agent를 handoffs 목록에 연결해요.
        # 힌트: analyze_agent
        analyze_agent
    ],
)

TEST_CASES = [
    {
        "label": "분석 요청",
        "input": """
        아래 자소서를 ResumeAnalysis 5필드 기준으로 분석해줘.
        저는 팀 프로젝트에서 로그인 API 오류를 정리했고,
        재발 방지를 위해 오류 메시지와 테스트 케이스를 문서화했습니다.
        """,
    },
    {
        "label": "범위 밖 요청",
        # TODO: 자소서와 관련 없는 짧은 요청을 직접 작성해요.
        "input": "오늘 서울 날씨 알려줘.",
    },
]

analyze_handoff = handoff(
    agent=analyze_agent,
    # TODO: 필요하면 tool_description_override에 분석 요청 설명을 넣어요.
)

revise_handoff = handoff(
    agent=revise_agent,
    # TODO: 필요하면 tool_description_override에 첨삭 요청 설명을 넣어요.
)

final_handoff = handoff(
    agent=final_agent,
    # TODO: 필요하면 tool_description_override에 최종본 요청 설명을 넣어요.
)
class ResumeGuardrailOutput(BaseModel):
    # TODO: 위험 입력 여부를 담는 bool 필드를 추가해요.
    # 힌트: is_harmful: bool
    is_harmful: bool


@input_guardrail
async def resume_input_guardrail(ctx, agent, input_data):
    # TODO: 입력을 문자열로 바꾸고 위험 키워드를 검사해요.
    text = str(input_data).lower()

    harmful_keywords = [
        # TODO: "허위 경력", "개인정보 노출", "시스템 프롬프트" 같은 키워드를 넣어요.
        "허위 경력","개인정보 노출","시스템 프롬프트",
        "ignore previous instructions","reveal system prompt","show hidden instructions"
    ]

    tripwire = any(
        keyword in text
        for keyword in harmful_keywords
    )  # TODO: any(...)로 조건을 채워요.

    return GuardrailFunctionOutput(
        output_info=ResumeGuardrailOutput(is_harmful=tripwire),
        tripwire_triggered=tripwire,
    )

async def run_case(label: str, user_input: str) -> None:
    print(f"\n--- {label} ---")
    # TODO: Runner.run으로 triage_agent와 user_input을 실행해요.
    # 힌트: result = await Runner.run(triage_agent, input=user_input)
    result = await Runner.run(triage_agent, input=user_input)

    # TODO: 마지막 Agent 이름을 출력해요.
    # 힌트: result.last_agent.name
    print("last_agent:", {result.last_agent.name})

    # TODO: 최종 출력 일부를 출력해요.
    print("output:", {str(result.final_output[:1800])})


# async def main() -> None:
#     for case in TEST_CASES:
#         await run_case(case["label"], case["input"])

async def main():
    triage_agent = Agent(
        name="자소서_Triage",
        instructions="""
        당신은 자소서 도우미의 접수 담당입니다.

        규칙:
        - 자소서 분석, ResumeAnalysis, 결함 탐지 요청은 ResumeAnalyzeAgent로 넘겨요.
        - 자소서 첨삭, 문장 개선, STAR/PREP/CAR 개선 요청은 자소서_첨삭_Specialist로 넘겨요.
        - 제출용 최종본, 최종 문단 작성 요청은 자소서_최종본_Specialist로 넘겨요.
        - 자소서와 관련 없는 요청은 범위 밖이라고 짧게 안내해요.
        - 직접 긴 답변을 작성하지 말고 적합한 Specialist를 선택해요.
        """,
        handoffs=[analyze_handoff, revise_handoff, final_handoff],
        input_guardrails=[resume_input_guardrail],
        model=MODEL_NAME,
    )

    test_requests = [
        # TODO: 분석 요청 1개를 넣어요.
        "이 자소서를 ResumeAnalysis 기준으로 분석해줘.",        
        # TODO: 첨삭 요청 1개를 넣어요.
        "이 자소서를 STAR 방식으로 첨삭해줘.",        
        # TODO: 최종본 요청 1개를 넣어요.
        "첨삭 결과를 반영해서 최종본을 작성해줘.",        
    ]

    for index, request in enumerate(test_requests, start=1):
        result = await Runner.run(triage_agent, request)
        print(f"[테스트 {index}] 담당 Agent:", result.last_agent.name)
        print(result.final_output[:200])


if __name__ == "__main__":
    asyncio.run(main())