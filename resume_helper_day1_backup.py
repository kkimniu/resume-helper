import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from pathlib import Path
from styles import STYLE_PRESETS, list_style_names

source = Path("resume_helper.py")
backup = Path("resume_helper_day1_backup.py")

# TODO: resume_helper.py가 있는지 확인해요.
# 힌트: source.exists()를 사용해요.
if source.exists():
    print("resume_helper.py 확인 완료")
else:
    print("resume_helper.py를 먼저 찾아요")

# TODO: 필요하면 백업 파일을 만들어요.
# 힌트: source.read_text(encoding="utf-8")와 backup.write_text(...)를 사용해요.
backup.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

current_style_key = "간결형"

def handle_style_command(user_input: str) -> str:
    parts = user_input.split(maxsplit=1)

    if len(parts) < 2:
        # TODO: 사용 가능한 스타일 이름을 출력하고 현재 스타일을 유지해요.
        print("사용 가능한 스타일:", list_style_names())
        return current_style_key

    style_key = parts[1].strip()

    if style_key in STYLE_PRESETS:
        # TODO: 선택된 스타일 이름을 로그로 출력해요.
        print(style_key)
        return style_key

    # TODO: 알 수 없는 스타일일 때 가능한 이름을 안내해요.
    print(f"알 수 없는 스타일입니다. 사용 가능한 스타일: {list_style_names()}")
    return current_style_key



PROMPT_CHAT = """
너는 한국 채용 시장에 특화된 자소서 첨삭 전문가로서 STAR, PREP, CAR 프레임과 NCS 역량 기반 분석을 활용하여 자기소개서를 평가하고,
추상적 표현, 정량 지표 부재, 직무 키워드 미스매치, 자기 자랑 단방향 서술, 내용 일관성 결여, 공통 템플릿 표현 등 6대 결함을 탐지하여 구체적인 개선 방향을 제시한다.
"""
def load_settings() -> dict[str, str | None]:
    # 여기에 .env를 읽는 코드를 채워요.
    load_dotenv()
    # 힌트: load_dotenv()
    return {
        "openai_key_exists":bool(os.getenv("OPENAI_API_KEY")),
        "anthropic_key_exists":  bool(os.getenv("ANTHROPIC_API_KEY")),
    }

def make_openai_client() -> OpenAI:
    # TODO: OpenAI 클라이언트를 만들어 반환해요.
    return OpenAI()

def make_claude_client() -> Anthropic:
    # TODO: Claude 클라이언트를 만들어 반환해요.
    return Anthropic()

# 학생 작성용 — 자소서 첨삭 역할 골격
RESUME_SYSTEM_PROMPT = """
너는 한국 채용 맥락을 이해하는 자소서 첨삭 전문가입니다.
사용자가 입력한 자기소개서 또는 지원동기를 읽고,
구체적인 개선 방향을 한국어로 제안합니다.

첨삭할 때 참고할 기준:
- 한국 자소서 기본 구조: 지원동기 → 직무역량 → 경험사례 → 성과 → 입사 후 포부
- 확인할 결함 패턴: 추상적인 표현, 직무와 무관한 경험 나열, 성과 및 수치 부족
- STAR 프레임(Situation, Task, Action, Result)을 우선 확인
- 블라인드 채용에서는 학교명, 출신지역, 가족관계, 나이 등의 개인정보 노출에 주의
"""

def get_sample_resume() -> str:
    # TODO: 본인 자소서가 없으면 대체 샘플 1개를 반환해요.
    return """
    저는 맡은 일을 열심히 하는 사람입니다.
    백엔드 개발자로 성장하고 싶고, 프로젝트에서도 책임감 있게 참여했습니다.
    입사 후 회사에 도움이 되는 개발자가 되겠습니다.
    """
# 학생 작성용 — OpenAI 첫 호출 골격
def ask_openai_once(sample_text: str) -> str:
    client = make_openai_client()

    # TODO: client.chat.completions.create(...) 호출을 작성해요.
    # 힌트: messages 배열에 system과 user를 넣어요.
    
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        max_completion_tokens=600,
        messages=[
            {"role":"system","content":RESUME_SYSTEM_PROMPT},
            {"role":"user","content":sample_text},
        ]
    )
    # TODO: choices[0].message.content에서 텍스트를 꺼내요.
    return response.choices[0].message.content

def ask_claude_once(sample_text: str) -> str:
    client = make_claude_client()

    # TODO: client.messages.create(...) 호출을 작성해요.
    # 힌트: system=RESUME_SYSTEM_PROMPT, messages=[{"role": "user", ...}]
    message = client.messages.create(
        model="claude-haiku-4.5-20251001",
        max_tokens=300,
        system=RESUME_SYSTEM_PROMPT,
        messages=[
            {"role":"user","content":sample_text},
        ]
    )

    # TODO: content[0].text에서 텍스트를 꺼내요.
    return message.content[0].text

# 학생 작성용 — 첫 실행 골격
def main() -> None:
    load_settings()
    sample_text = get_sample_resume()
    provider = input("사용할 제공사(openai/claude)를 입력하세요: ").strip().lower()

    if provider == "openai":
        result = ask_openai_once(sample_text)
    elif provider == "claude":
        result = ask_claude_once(sample_text)
    else:
        print("openai 또는 claude 중 하나를 입력해요.")
        return

    print("[자소서 도우미 첫 응답]")
    print(result[:1000])

def chat_loop():
    print("자소서 도우미를 시작합니다./style로 스타일 /help로 도움말, /quit으로 종료합니다.")

    while True:
        user_input = input("자소서 입력 > ")
        command = user_input.strip()
        # 여기에 /help 분기 코드를 채워요. (3단계)
        # 여기에 /quit 분기 코드를 채워요. (4단계)
        if command == "/help":
            help_text = """
                [사용 방법]
                자소서 또는 지원동기를 입력하세요.
                입력한 내용을 첨삭해 줍니다.
                개인정보는 입력하지 마세요.
                종료하려면 /quit 을 입력하세요.
            """
            print(help_text)
            continue
        elif command.startswith("/style"):
            current_style_key = handle_style_command(user_input)
            continue
        elif command == "/quit":
            print("종료")
            break
        # TODO: Chat Completions에 보낼 messages 배열을 만들어요.
        # 힌트: system 역할과 user 역할을 모두 포함해야 해요.
        messages = [
            {
                # 여기에 system 메시지를 채워요.
                "role" : "system",
                "content": STYLE_PRESETS[current_style_key]["system"],
            },
            {
                # 여기에 user 메시지를 채워요.
                "role" : "user",
                "content":user_input,
            }
        ]

        # TODO: client.chat.completions.create(...) 호출을 채워요.
        # 힌트: model, messages, max_completion_tokens를 넣어요.
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            max_completion_tokens=600,
            messages=messages
        )

        # TODO: 응답 텍스트만 꺼내 출력해요.
        # 힌트: choices[0].message.content 경로를 사용해요.
        answer = response.choices[0].message.content
        print(answer)


if __name__ == "__main__":
    chat_loop()