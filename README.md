
# 나만의 자소서 도우미

## 프로젝트 목적

이 프로젝트는 자기소개서 초안을 입력하면 작성 스타일에 따라 첨삭하고, 자소서의 구조와 결함을 점검하는 CLI 기반 도우미입니다.

한국식 자기소개서에서 자주 발생하는 문제인 추상적 표현, 정량 근거 부족, 직무 키워드 부족, 블라인드 채용 위험 표현을 확인할 수 있도록 구성했습니다. STAR, PREP, CAR 구조를 기준으로 분석, 첨삭, 최종본 작성 흐름을 지원합니다.

---

## 주요 기능

### 1. 스타일 기반 첨삭

`/style` 명령으로 사용 가능한 작성 스타일을 확인하고, `/set 스타일명`으로 첨삭 스타일을 변경할 수 있습니다.

지원 스타일 예시:

- 간결형
- 스토리형
- 직무맞춤형
- 성과수치형
- 직무근거형

### 2. 로컬 규칙 기반 분석

`/analyze` 명령으로 자소서 원문과 NCS/JD 키워드를 입력하면 규칙 기반 분석 결과를 확인하고 `analyze_result.json`으로 저장합니다.

점검 항목:

- STAR/PREP 프레임 단서
- NCS/JD 키워드 누락
- 블라인드 채용 위반 표현
- 일반화 표현

### 3. Agent 라우팅

`/agent` 명령으로 분석, 첨삭, 최종본 요청을 Triage Agent가 적절한 Specialist Agent로 라우팅합니다.

구성 Agent:

- 자소서 분석 Specialist
- 자소서 첨삭 Specialist
- 자소서 최종본 Specialist
- 자소서 도우미 Triage

### 4. AI 1차 필터 점검

`/filter` 명령으로 자소서를 AI 1차 필터 관점에서 점검합니다.

기본 검증 항목:

- STAR 구조 충족 여부
- 정량 근거 포함 여부
- NCS 직무 키워드 밀도

### 5. 블라인드 채용 위험 표현 점검

`/blind` 명령으로 나이, 학교, 주소, 전화번호 등 블라인드 채용에서 조심해야 할 표현 후보를 찾습니다.

---

## 프로젝트 구조

```text
resume-helper/
├── config.py
├── styles.py
├── resume_tool.py
├── resume_agents.py
├── resume_helper.py
├── README.md
├── .env
└── .gitignore
```

### 파일 역할

| 파일 | 역할 |
|---|---|
| `resume_helper.py` | CLI 메인 실행 파일 |
| `config.py` | 환경변수 로딩, 모델명 관리 |
| `styles.py` | `/style`, `/set`에 사용하는 스타일 프리셋 |
| `resume_tool.py` | 자소서 분석, AI 필터, 블라인드 점검, Guardrail |
| `resume_agents.py` | 분석/첨삭/최종본 Agent와 Triage 구성 |

---

## 실행 환경

- Python: 3.10 이상
- 실행 도구: uv
- 주요 패키지:
  - openai
  - openai-agents
  - python-dotenv
  - pydantic

모델명과 SDK 버전은 학습 당일 기준으로 다시 확인하는 것을 권장합니다.

---

## 환경변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 넣습니다.

```env
OPENAI_API_KEY=여기에_API_KEY를_입력하세요
```

현재 코드에서는 `config.py`의 `MODEL_NAME` 값을 사용합니다.

```python
MODEL_NAME = "gpt-5.4-nano"
```

API 키는 코드에 직접 작성하지 않고 `.env`에서만 불러옵니다.

---

## 실행 방법

```powershell
uv run python resume_helper.py
```

또는 가상환경을 직접 실행하는 경우:

```powershell
.venv\Scripts\python.exe resume_helper.py
```

---

## 명령어

| 명령어 | 설명 |
|---|---|
| `/help` | 사용 가능한 명령어를 확인합니다. |
| `/style` | 사용 가능한 스타일 목록을 확인합니다. |
| `/set 스타일명` | 첨삭 스타일을 변경합니다. |
| `/analyze` | 로컬 규칙 기반 자소서 분석을 실행합니다. |
| `/agent` | Agent 라우팅으로 분석/첨삭/최종본 요청을 처리합니다. |
| `/filter` | AI 1차 필터 기준으로 자소서를 점검합니다. |
| `/blind` | 블라인드 채용 위험 표현을 점검합니다. |
| `/quit` | 프로그램을 종료합니다. |

---

## 예시 입출력

### 입력 예시

```text
지원 직무: 백엔드 개발자
문항: 프로젝트 경험을 통해 문제를 해결한 경험을 작성하세요.
초안: 저는 팀 프로젝트에서 로그인 API 오류를 분석했고, 오류 메시지와 테스트 케이스를 문서화하여 같은 문제가 반복되지 않도록 했습니다.
```

### 명령 흐름

```text
/style
/set 스토리형
/filter
/blind
/agent
```

### 출력 예시

```text
[AI 1차 필터 점검 결과]
- STAR 구조는 일부 드러나지만 상황과 결과가 더 구체화되면 좋습니다.
- 정량 근거가 부족하므로 오류 감소율, 테스트 케이스 수, 문서화 범위를 추가하는 것이 좋습니다.
- NCS 직무 키워드는 API, 테스트, 문서화가 드러나지만 협업과 문제 해결 역량을 더 명확히 표현하면 좋습니다.
```

```text
[블라인드 채용 점검 결과]
블라인드 채용 위험 표현 후보가 발견되지 않았어요.
```

---

## 보안 주의사항

`.env`와 실제 자소서 원문은 GitHub에 올리지 않습니다.

`.gitignore`에는 아래 항목을 포함하는 것을 권장합니다.

```gitignore
.env
.venv/
__pycache__/
*.pyc

# 자소서 원문과 민감 결과물
*.txt
resumes/
outputs/*.json
outputs/*.log
logs/

# 로컬 제출 압축 파일
submit_local/
```

GitHub push 전 아래 명령으로 민감 파일이 포함되었는지 확인합니다.

```powershell
git status --short
git diff --stat
```

---

## 제출 기록

- 저장소 공개 범위: TODO
- 마지막 commit 메시지: TODO
- push 시각: TODO
- push 결과: TODO
- 로컬 제출 대체 사유: 해당 없음
- 민감 파일 점검: `.env`, 자소서 원문, 실행 로그가 commit에 포함되지 않음

---

## 5일 회고

- Day 1: CLI 대화 루프를 만들면서 사용자 입력을 반복 처리하는 흐름을 익혔습니다.
- Day 2: `/style` 기능을 통해 system 프롬프트를 스타일별로 분리하는 방법을 익혔습니다.
- Day 3: `ResumeAnalysis`와 `/analyze`를 통해 자소서 분석 결과를 구조화하는 방법을 익혔습니다.
- Day 4: 분석, 첨삭, 최종본 Agent를 분리하고 Triage Agent로 라우팅하는 구조를 만들었습니다.
- Day 5: AI 1차 필터와 블라인드 채용 점검 기능을 추가하고 제출 가능한 형태로 정리했습니다.

---

## 남은 위험

- API 키가 GitHub에 올라가지 않도록 `.env`를 반드시 `.gitignore`에 포함해야 합니다.
- 긴 자소서 입력 시 토큰 사용량이 증가할 수 있으므로 입력 길이 제한이나 요약 기능이 필요합니다.
- 예외 메시지를 그대로 출력하기보다 사용자에게 이해하기 쉬운 오류 안내로 바꾸는 개선이 필요합니다.
- Agent 이름에 한글이 포함되어 SDK에서 tool name 경고가 발생할 수 있으므로, 필요하면 Agent 이름을 영문으로 변경할 수 있습니다.

---

## 9주차 TODO

- Streamlit 화면으로 전환할 때 `analyze_resume()`, `check_resume_ai_filter()`, `check_blind_risks()` 함수를 재사용합니다.
- 화면 구성 후보:
  - 자소서 입력창
  - 스타일 선택 박스
  - 분석 실행 버튼
  - AI 필터 실행 버튼
  - 블라인드 점검 결과 영역
  - Agent 응답 출력 영역

---