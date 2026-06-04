import os
from dotenv import load_dotenv
from agents import Agent
from agents import Runner
import asyncio
# TODO: Agents SDK에서 필요한 Agent와 Runner를 임포트해요.
# 힌트: from agents import Agent, Runner
MODEL_NAME = "gpt-4o-mini"
load_dotenv()


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
        "Triage가 볼 첨삭 Agent 설명을 채워요. "
        "STAR/PREP/CAR 기준으로 문장 개선을 요청할 때 사용한다고 적습니다."
    ),
    instructions=""" 여기에 첨삭 역할 지시문을 작성해요.
    6대 결함 패턴을 점검해요.
    한 번에 완성본을 쓰기보다 개선 제안을 먼저 만들어요.
    허위 경력 생성은 거절해요.
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


async def main() -> None:
    for case in TEST_CASES:
        await run_case(case["label"], case["input"])


if __name__ == "__main__":
    check_env()
    asyncio.run(main())