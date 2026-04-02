"""
Specyn 런타임이 Codex를 CLI 또는 HTTP API 형태로 호출할 때 공통으로 사용하는 실행 어댑터다.
프롬프트 전달, 출력 수집, 생성 파일 추출을 `CodexExecutionResult` 구조로 통일해 상위 로직이 실행 방식 차이를 신경 쓰지 않게 한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import shlex
import subprocess
import urllib.request


@dataclass(slots=True)
class CodexExecutionResult:
    """
    단일 실행 단계나 외부 호출 결과를 구조화해 전달하기 위한 결과 모델이다.

    Attributes:
        success: 인스턴스가 내부적으로 유지하는 success 관련 상태다.
        output: 인스턴스가 내부적으로 유지하는 출력 관련 상태다.
        generated_files: 실행 중 생성된 파일 경로 목록이다.
    """
    success: bool
    output: str
    generated_files: list[str]


def execute_cli(prompt: str, workspace: Path) -> CodexExecutionResult:
    """
    도구 계층에서 CLI 실행 흐름을 수행한다.

    주요 흐름은 `format()`, `run()`, `splitlines()`, `CodexExecutionResult()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        prompt: LLM 또는 Codex에 전달할 프롬프트 전문이다.
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.

    Returns:
        함수에서 조립한 `CodexExecutionResult` 타입 결과다.
    """
    template = os.environ.get("CODEX_COMMAND_TEMPLATE", "codex exec --json --model {model} -C {workspace} --skip-git-repo-check")
    model = os.environ.get("CODEX_MODEL", os.environ.get("OPENAI_MODEL", "gpt-5.4"))
    command = template.format(workspace=str(workspace), model=model)
    process = subprocess.run(
        shlex.split(command),
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    stdout = process.stdout.decode("utf-8").strip()
    stderr = process.stderr.decode("utf-8").strip()
    text = stdout or stderr

    generated_files = [
        line.removeprefix("FILE:").strip() for line in text.splitlines() if line.startswith("FILE:")
    ]
    return CodexExecutionResult(
        success=process.returncode == 0,
        output=text,
        generated_files=generated_files,
    )


def execute_api(prompt: str, api_url: str, workspace: Path | None = None) -> CodexExecutionResult:
    """
    도구 계층에서 API 실행 흐름을 수행한다.

    주요 흐름은 `Request()`, `urlopen()`, `read()`, `CodexExecutionResult()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        prompt: LLM 또는 Codex에 전달할 프롬프트 전문이다.
        api_url: 문자열 입력값이다.
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.

    Returns:
        함수에서 조립한 `CodexExecutionResult` 타입 결과다.
    """
    payload = json.dumps(
        {
            "prompt": prompt,
            "workspacePath": str(workspace) if workspace else None,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url=api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:  # nosec - controlled local usage
        body = json.loads(response.read().decode("utf-8"))
    return CodexExecutionResult(
        success=True,
        output=json.dumps(body, ensure_ascii=False, indent=2),
        generated_files=body.get("generatedFiles", []),
    )
