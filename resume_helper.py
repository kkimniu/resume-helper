

import asyncio
import sys

from agents import InputGuardrailTripwireTriggered
from agents import Runner

from config import MODEL_NAME
from config import ini_env

from resume_agents import triage_agent

from resume_tool import CHECK_ITEMS
from resume_tool import analyze_resume
from resume_tool import check_blind_risks
from resume_tool import check_resume_ai_filter
from resume_tool import format_blind_report
from resume_tool import save_analysis

from styles import STYLES
from styles import list_style_names
from styles import print_available_styles

from openai import OpenAI

client = OpenAI()
current_style_key = "간결형"


COMMANDS = {
    "/help": "사용 가능한 명령어를 보여줍니다.",
    "/quit": "자소서 도우미를 종료합니다.",
    "/style": "사용 가능한 스타일 목록을 보여줍니다.",
    "/set": "스타일을 변경합니다. 예: /set 스토리형",
    "/analyze": "로컬 규칙 기반으로 자소서를 분석합니다.",
    "/agent": "Agent 라우팅으로 분석/첨삭/최종본을 처리합니다.",
    "/filter": "AI 1차 필터 기준으로 자소서를 최종 점검합니다.",
    "/blind": "블라인드 채용 위험 표현을 점검합니다.",
}


def show_help() -> None:
    print("\n[사용 가능한 명령어]")
    for command, description in COMMANDS.items():
        print(f"{command:10s} - {description}")
    print()


def show_styles() -> None:
    print("\n[사용 가능한 스타일]")
    print_available_styles()
    print(f"\n현재 스타일: {current_style_key}\n")


def change_style(user_input: str) -> None:
    global current_style_key
    parts = user_input.split(maxsplit=1)

    if len(parts) < 2:
        print("변경할 스타일 이름을 입력하세요.")
        print(f"가능한 스타일: {list_style_names()}")
        return

    style_key = parts[1].strip()

    if style_key not in STYLES:
        print(f"알 수 없는 스타일입니다. 가능: {list_style_names()}")
        return

    current_style_key = style_key
    print(f"스타일이 '{style_key}'로 변경되었습니다.")


def ask_openai_once(resume_text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": STYLES[current_style_key]["system"],
        },
        {
            "role": "user",
            "content": resume_text,
        },
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_completion_tokens=600,
        messages=messages,
    )

    return response.choices[0].message.content

def run_ai_filter() -> None:
    resume_text = input("점검할 자소서 > ").strip()

    result = check_resume_ai_filter(
        resume_text,
        CHECK_ITEMS,
    )

    print("\n[AI 1차 필터 점검 결과]")
    print(result)


def run_blind_check() -> None:
    resume_text = input("점검할 자소서 > ").strip()

    found = check_blind_risks(resume_text)
    report = format_blind_report(found)

    print("\n[블라인드 채용 점검 결과]")
    print(report)
    
def run_local_analyze() -> None:
    resume_text = input("자소서 원문 > ").strip()
    keyword_text = input("NCS/JD 키워드, 쉼표 구분 > ").strip()

    analysis = analyze_resume(resume_text, keyword_text)
    save_analysis(analysis)

    print("\n[분석 결과]")
    print(analysis.model_dump())


async def run_agent_command() -> None:
    user_input = input("Agent에게 요청할 내용 > ").strip()

    if not user_input:
        print("요청 내용을 입력하세요.")
        return

    try:
        result = await Runner.run(
            triage_agent,
            input=user_input,
        )

        print(f"\n[{result.last_agent.name}]")
        print(result.final_output)

    except InputGuardrailTripwireTriggered:
        print("안전하지 않은 입력이 감지되었습니다.")
        print("자소서 관련 요청을 다시 입력하세요.")

    except Exception as error:
        print(f"오류가 발생했습니다: {type(error).__name__}")
        print(error)


def main() -> None:
    print()
    print("=" * 50)
    print("   나만의 자소서 도우미")
    print("=" * 50)

    print(f"모델: {MODEL_NAME}")
    print(f"현재 스타일: {current_style_key}")
    print("/help 로 명령어를 확인하세요.\n")

    while True:
        user_input = input("자소서 입력 > ").strip()

        if not user_input:
            continue

        if user_input == "/quit":
            print("자소서 도우미를 종료합니다.")
            break

        if user_input == "/help":
            show_help()
            continue

        if user_input == "/style":
            show_styles()
            continue

        if user_input.startswith("/set"):
            change_style(user_input)
            continue

        if user_input == "/analyze":
            run_local_analyze()
            continue

        if user_input == "/agent":
            asyncio.run(run_agent_command())
            continue

        if user_input == "/filter":
            run_ai_filter()
            continue

        if user_input == "/blind":
            run_blind_check()
            continue

        if user_input.startswith("/"):
            print(f"알 수 없는 명령어입니다: {user_input}")
            print("/help 로 사용 가능한 명령어를 확인하세요.")
            continue

        try:
            answer = ask_openai_once(user_input)
            print(answer)

        except Exception as error:
            print(f"오류가 발생했습니다: {type(error).__name__}")
            print(error)


if __name__ == "__main__":
    if not ini_env():
        sys.exit(1)  
    main()