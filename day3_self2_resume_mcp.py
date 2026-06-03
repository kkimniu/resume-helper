import 


def run_cli() -> None:
    print("자소서 도우미입니다. /analyze 를 입력해요.")
    command = input("명령: ").strip()

    if command == "/analyze":
        resume_text = input("자소서 원문: ").strip()
        keyword_text = input("NCS/JD 키워드(쉼표 구분): ").strip()
        # TODO: 여기에 analyze_resume(...) 호출을 채워요.
        # analyze_resume()
        print("분석 흐름을 연결하세요.")
    else:
        print("지원하는 명령: /analyze")
def detect_flaws(resume_text: str, required_keywords: list[str]) -> list[str]:
    defects: list[str] = []
    sentences = [part.strip() for part in resume_text.split(".")]

    # TODO: STAR/PREP 단서가 부족한 경우를 defects에 추가해요.
    # 힌트: "상황", "과제", "행동", "결과", "근거", "이유" 같은 단어를 확인해요.

    # TODO: NCS/JD 키워드 누락 여부를 확인해요.
    # 힌트: required_keywords 중 resume_text에 없는 키워드를 찾아요.

    # TODO: 공백 문장, 일반화 표현, 수동태 남발 조건을 채워요.
    return defects
