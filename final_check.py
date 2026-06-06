import subprocess
from pathlib import Path


def check_resume_not_in_git_history() -> bool:
    """자소서 원문이 Git 추적 대상에 들어갔는지 점검하는 함수예요."""
    result = subprocess.run(
        ["git", "log", "--all", "--", "*.txt"],
        capture_output=True,
        text=True,
    )    
    return result.stdout.strip() == ""


def check_required_files() -> bool:
    """제출 필수 파일이 있는지 확인하는 함수예요."""
    required = ["README.md", ".gitignore", "resume_helper.py", "resume_agents.py"]
    for file in required:
        if not Path(file).exists():
            return False
    return True