from agents import Agent
from agents import handoff

from config import MODEL_NAME

from resume_tool import resume_input_guardrail



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
    name="자소서_분석_Specialist",
    # TODO: Triage가 이 Agent를 고를 때 참고할 설명을 채워요.
    # 힌트: 자소서 분석, ResumeAnalysis 5필드, 6대 결함 탐지 요청
    handoff_description="자소서 분석, ResumeAnalysis 5필드, 6대 결함 탐지 요청",
    instructions="""
    당신은 자기소개서 분석 전문가입니다.
    분석 기준:
    - 성장: 성장 과정이 구체적인 경험과 함께 설명되었는가
    - 동기: 지원 동기가 직무와 연결되어 있는가
    - 포부: 입사 후 목표와 계획이 명확한가
    - 경험: 직무 관련 경험과 역할이 드러나는가
    - 성공실패: 성공 또는 실패 경험에서 배운 점이 있는가

    결함 점검:
    - 추상적 표현
    - 수치 부재
    - 복붙 흔적
    - 직무 불일치
    - NCS 미반영
    - 블라인드 위반

    출력은 짧은 분석 요약과 결함 태그 중심으로 작성해요.
    """,
    model=MODEL_NAME,
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

analyze_handoff = handoff(
    agent=analyze_agent,
    tool_description_override="자소서 분석, ResumeAnalysis 5필드, 결함 탐지 요청에 사용합니다.",
)

revise_handoff = handoff(
    agent=revise_agent,
    tool_description_override="자소서 첨삭, STAR/PREP/CAR 기준 문장 개선 요청에 사용합니다.",
)

final_handoff = handoff(
    agent=final_agent,
    tool_description_override="첨삭 결과를 반영한 제출용 자기소개서 최종본 작성 요청에 사용합니다.",
)
triage_agent = Agent(
    name="자소서_도우미_Specialist",
    instructions="""
    당신은 자소서 도우미의 접수 담당입니다.

    규칙:
    - 사용자가 자소서 분석, ResumeAnalysis, 결함 탐지를 요청하면 분석 Agent로 넘겨요.
    - 사용자가 첨삭, 문장 개선, STAR, PREP, CAR 기준 수정을 요청하면 첨삭 Agent로 넘겨요.
    - 사용자가 최종본, 제출용 문단, 완성본 작성을 요청하면 최종본 Agent로 넘겨요.
    - 날씨, 잡담, 일반 검색처럼 자소서와 관련 없는 요청은 범위 밖이라고 안내해요.
    - 직접 긴 분석, 첨삭, 최종본을 작성하지 말고 적합한 Specialist를 선택해요.
    """,
    handoffs=[analyze_handoff, revise_handoff, final_handoff],
    input_guardrails=[resume_input_guardrail],
    model=MODEL_NAME,
)

