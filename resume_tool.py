# (학생 따라하기) day3_self1_resume_tool.py
from pydantic import BaseModel, Field
from enum import Enum

class ResumeAnalysis(BaseModel):
    # TODO: 성장 과정 필드의 의미를 한 줄로 적어요.
    growth: str = Field(..., description="성장 과정과 개발 계기")

    # TODO: 지원 동기 필드의 의미를 한 줄로 적어요.
    motivation: str = Field(..., description="지원 동기와 직무 선택 이유")

    # TODO: 입사 후 포부 필드의 의미를 한 줄로 적어요.
    aspiration: str = Field(..., description="입사 후 목표와 성장 계획")

    # TODO: 직무 경험 필드의 의미를 한 줄로 적어요.
    experience: str = Field(..., description="직무 관련 경험과 프로젝트")

    # TODO: 성공 또는 실패 경험 필드의 의미를 한 줄로 적어요.
    success_failure: str = Field(..., description="성공 또는 실패 경험과 배운 점")

class DefectType(str, Enum):
    # TODO: "추상표현" 값을 채워요.
    abstract_expression = "추상표현"

    # TODO: "정량부재" 값을 채워요.
    missing_metric = "정량부재"

    # TODO: "키워드미스매치" 값을 채워요.
    keyword_mismatch = "키워드미스매치"

    # TODO: "자기자랑" 값을 채워요.
    self_promotion = "자기자랑"

    # TODO: "일관성결여" 값을 채워요.
    inconsistency = "일관성결여"

    # TODO: "공통템플릿" 값을 채워요.
    generic_template = "공통템플릿"

def build_sample_payload() -> dict[str, str]:
# TODO: 5개 필드의 예시 값을 직접 채워요.
    return {
        "growth": "게임 개발에 관심을 가지며 개발자의 꿈을 키웠다.",
        "motivation": "Java와 웹 개발 경험을 통해 백엔드 개발자가 되기로 결심했다.",
        "aspiration": "실무 역량을 갖춘 백엔드 개발자로 성장하고 싶다.",
        "experience": "중고거래 웹사이트와 모의투자 웹사이트 프로젝트를 수행했다.",
        "success_failure": "댓글 기능 구현 과정에서 발생한 문제를 해결하며 성장했다.",
    }

def validate_payload() -> None:
# 여기에 ResumeAnalysis.model_validate(...) 코드를 채워요.
    analysis = ResumeAnalysis.model_validate(build_sample_payload())
    print(analysis.model_dump())

if __name__ == "__main__":
    payload = build_sample_payload()
    # TODO: validate_payload()에서 model_validate를 호출하게 만들어요.
    validate_payload()
    # 여기에 schema의 properties 키를 출력하는 코드를 채워요.
    print(ResumeAnalysis.model_json_schema()["properties"].keys())