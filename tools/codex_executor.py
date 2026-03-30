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
    success: bool
    output: str
    generated_files: list[str]


def execute_cli(prompt: str, workspace: Path) -> CodexExecutionResult:
    template = os.environ.get("CODEX_COMMAND_TEMPLATE", "codex exec --json --cwd {workspace}")
    command = template.format(workspace=str(workspace))
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
