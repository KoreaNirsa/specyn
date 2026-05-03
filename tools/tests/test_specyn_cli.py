"""
`specyn cli` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import local_sdd_runtime, prompt_compiler, specyn


def test_cmd_init_spec_writes_spec_kit_file_names(tmp_path: Path) -> None:
    args = type("Args", (), {
        "project_id": "sample-service",
        "output_dir": str(tmp_path),
        "overwrite": False,
    })()

    exit_code = specyn.cmd_init_spec(args)

    assert exit_code == 0
    assert (tmp_path / "spec.md").exists()
    assert (tmp_path / "tasks.md").exists()
    assert (tmp_path / "plan.md").exists()
    assert not (tmp_path / "product.md").exists()
    assert not (tmp_path / "test.md").exists()
    assert not (tmp_path / "agent.md").exists()


def test_cmd_run_local_returns_generated_file_summary(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_run_local_returns_generated_file_summary` 시나리오를 검증한다.

    주요 흐름은 `type()`, `type('Args', (), {'spec_dir': 'specs/001-sample-service', 'project_id': 'sample-service', 'workspace': '.workspace/sample-service', 'backend_url': None, 'rag_enabled': False, 'runtime': 'local'})()`, `cmd_run()`, `readouterr()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    monkeypatch.setattr(prompt_compiler, "AGENT_DIR", Path("agents"))
    monkeypatch.setattr(local_sdd_runtime, "PROMPT_ROOT_DIR", tmp_path / ".specyn" / "prompts")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_DOCS_DIR", Path("docs") / "generated")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_AI_SERVER_DIR", Path("ai-server") / "app" / "generated")
    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)

    args = type("Args", (), {
        "spec_dir": "specs/001-sample-service",
        "project_id": "sample-service",
        "workspace": ".workspace/sample-service",
        "backend_url": None,
        "rag_enabled": False,
        "runtime": "local",
    })()

    exit_code = specyn.cmd_run(args)
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 1
    assert payload["status"] == "BLOCKED"
    assert payload["projectId"] == "sample-service"
    assert payload["runtime"] == "local"
    assert payload["outputRoot"] == "projects/sample-service"
    assert "frontend/src/generated/sample-service/GeneratedProjectPage.tsx" in payload["generatedFiles"]


def test_cmd_setup_openapi_updates_env_and_logs_in(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_setup_openapi_updates_env_and_logs_in` 시나리오를 검증한다.

    주요 흐름은 `iter()`, `next()`, `type()`, `type('Args', (), {'auth_mode': 'openapi', 'model': 'gpt-5.4', 'api_key': 'sk-test-1234', 'chatgpt_action': None, 'install_codex': 'yes', 'non_interactive': True, 'browser_login': False})()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    env_file = tmp_path / ".env"
    env_example = tmp_path / ".env.example"
    env_example.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")
    env_file.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")

    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(specyn, "ENV_FILE", env_file)
    monkeypatch.setattr(specyn, "ENV_EXAMPLE_FILE", env_example)
    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    compose_file = tmp_path / "docker-compose.local.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setattr(specyn, "DASHBOARD_COMPOSE_FILE", compose_file)
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/docker" if binary == "docker" else None)
    monkeypatch.setattr(specyn, "docker_daemon_status", lambda: (True, "24.0.0"))
    monkeypatch.setattr(specyn, "ensure_codex_in_agent", lambda install_if_missing: (True, "codex 0.118.0"))

    login_states = iter([(False, "not logged in"), (True, "logged in with api key")])
    monkeypatch.setattr(specyn, "codex_login_status", lambda: next(login_states))

    calls: list[tuple[str, str | None]] = []
    monkeypatch.setattr(specyn, "codex_logout", lambda: calls.append(("logout", None)) or 0)
    monkeypatch.setattr(
        specyn,
        "codex_login_with_api_key",
        lambda api_key: calls.append(("login-api", api_key)) or 0,
    )

    args = type("Args", (), {
        "auth_mode": "openapi",
        "model": "gpt-5.4",
        "api_key": "sk-test-1234",
        "chatgpt_action": None,
        "install_codex": "yes",
        "non_interactive": True,
        "browser_login": False,
    })()

    exit_code = specyn.cmd_setup(args)
    output = json.loads(capsys.readouterr().out)
    env_text = env_file.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "SPECYN_AUTH_MODE=openapi" in env_text
    assert "OPENAI_API_KEY=sk-test-1234" in env_text
    assert "CODEX_MODEL=gpt-5.4" in env_text
    assert calls == [("logout", None), ("login-api", "sk-test-1234")]
    assert output["authMode"] == "openapi"
    assert output["codexInstalledInDocker"] is True


def test_cmd_setup_chatgpt_relogin_uses_cached_state(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_setup_chatgpt_relogin_uses_cached_state` 시나리오를 검증한다.

    주요 흐름은 `iter()`, `next()`, `type()`, `type('Args', (), {'auth_mode': 'chatgpt', 'model': 'gpt-5.4', 'api_key': None, 'chatgpt_action': 'relogin', 'install_codex': 'yes', 'non_interactive': True, 'browser_login': False})()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    env_file = tmp_path / ".env"
    env_example = tmp_path / ".env.example"
    env_example.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")
    env_file.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")

    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(specyn, "ENV_FILE", env_file)
    monkeypatch.setattr(specyn, "ENV_EXAMPLE_FILE", env_example)
    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    compose_file = tmp_path / "docker-compose.local.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setattr(specyn, "DASHBOARD_COMPOSE_FILE", compose_file)
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/docker" if binary == "docker" else None)
    monkeypatch.setattr(specyn, "docker_daemon_status", lambda: (True, "24.0.0"))
    monkeypatch.setattr(specyn, "ensure_codex_in_agent", lambda install_if_missing: (True, "codex 0.118.0"))

    login_states = iter([(True, "logged in"), (True, "logged in")])
    monkeypatch.setattr(specyn, "codex_login_status", lambda: next(login_states))

    calls: list[str] = []
    monkeypatch.setattr(specyn, "codex_logout", lambda: calls.append("logout") or 0)
    monkeypatch.setattr(
        specyn,
        "codex_login_with_chatgpt",
        lambda device_auth: calls.append("login-chatgpt-device" if device_auth else "login-chatgpt-browser") or 0,
    )

    args = type("Args", (), {
        "auth_mode": "chatgpt",
        "model": "gpt-5.4",
        "api_key": None,
        "chatgpt_action": "relogin",
        "install_codex": "yes",
        "non_interactive": True,
        "browser_login": False,
    })()

    exit_code = specyn.cmd_setup(args)
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert calls == ["logout", "login-chatgpt-device"]
    assert output["authMode"] == "chatgpt"
    assert output["codexLoginCached"] is True


def test_cmd_setup_chatgpt_interactive_defaults_to_browser_login(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_setup_chatgpt_interactive_defaults_to_browser_login` 시나리오를 검증한다.

    주요 흐름은 `iter()`, `next()`, `type()`, `type('Args', (), {'auth_mode': 'chatgpt', 'model': 'gpt-5.4', 'api_key': None, 'chatgpt_action': 'relogin', 'install_codex': 'yes', 'non_interactive': False, 'browser_login': False})()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    env_file = tmp_path / ".env"
    env_example = tmp_path / ".env.example"
    env_example.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")
    env_file.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")

    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(specyn, "ENV_FILE", env_file)
    monkeypatch.setattr(specyn, "ENV_EXAMPLE_FILE", env_example)
    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    compose_file = tmp_path / "docker-compose.local.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setattr(specyn, "DASHBOARD_COMPOSE_FILE", compose_file)
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/docker" if binary == "docker" else None)
    monkeypatch.setattr(specyn, "docker_daemon_status", lambda: (True, "24.0.0"))
    monkeypatch.setattr(specyn, "ensure_codex_in_agent", lambda install_if_missing: (True, "codex 0.118.0"))
    monkeypatch.setattr(specyn, "prompt_choice", lambda *args, **kwargs: "browser")

    login_states = iter([(True, "logged in"), (True, "logged in")])
    monkeypatch.setattr(specyn, "codex_login_status", lambda: next(login_states))

    calls: list[str] = []
    monkeypatch.setattr(specyn, "codex_logout", lambda: calls.append("logout") or 0)
    monkeypatch.setattr(
        specyn,
        "codex_login_with_chatgpt",
        lambda device_auth: calls.append("login-chatgpt-device" if device_auth else "login-chatgpt-browser") or 0,
    )

    args = type("Args", (), {
        "auth_mode": "chatgpt",
        "model": "gpt-5.4",
        "api_key": None,
        "chatgpt_action": "relogin",
        "install_codex": "yes",
        "non_interactive": False,
        "browser_login": False,
    })()

    exit_code = specyn.cmd_setup(args)
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert calls == ["logout", "login-chatgpt-browser"]
    assert output["chatgptLoginMethod"] == "browser"


def test_codex_login_with_chatgpt_uses_host_codex_for_browser_flow(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `codex_login_with_chatgpt_uses_host_codex_for_browser_flow` 시나리오를 검증한다.

    주요 흐름은 `Completed()`, `codex_login_with_chatgpt()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    calls: list[tuple[list[str], str | None]] = []

    class Completed:
        """
        도구 모듈 테스트에서 사용되는 `Completed` 클래스다.
        """
        returncode = 0

    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/codex" if binary == "codex" else None)
    monkeypatch.setattr(
        specyn,
        "run_command",
        lambda command, **kwargs: calls.append((command, kwargs.get("env", {}).get("CODEX_HOME"))) or Completed(),
    )

    exit_code = specyn.codex_login_with_chatgpt(device_auth=False)

    assert exit_code == 0
    assert calls == [(["codex", "login"], str(specyn.CODEX_HOME_DIR))]


def test_codex_login_with_chatgpt_uses_npx_when_host_codex_is_missing(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `codex_login_with_chatgpt_uses_npx_when_host_codex_is_missing` 시나리오를 검증한다.

    주요 흐름은 `Completed()`, `codex_login_with_chatgpt()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    calls: list[list[str]] = []

    class Completed:
        """
        도구 모듈 테스트에서 사용되는 `Completed` 클래스다.
        """
        returncode = 0

    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/npx" if binary == "npx" else None)
    monkeypatch.setattr(
        specyn,
        "run_command",
        lambda command, **kwargs: calls.append(command) or Completed(),
    )

    exit_code = specyn.codex_login_with_chatgpt(device_auth=False)

    assert exit_code == 0
    assert calls == [["npx", "@openai/codex@latest", "login"]]


def test_cmd_sample_up_reports_missing_generated_runtime(capsys, monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_sample_up_reports_missing_generated_runtime` 시나리오를 검증한다.

    주요 흐름은 `type()`, `type('Args', (), {'detached': True})()`, `cmd_sample_up()`, `readouterr()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        capsys: capsys과(와) 관련된 입력값이다.
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    monkeypatch.setattr(specyn, "SAMPLE_COMPOSE_FILE", tmp_path / "projects" / "sample-service" / "docker-compose.local.yml")

    args = type("Args", (), {
        "detached": True,
    })()

    exit_code = specyn.cmd_sample_up(args)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "SAMPLE_RUNTIME_NOT_GENERATED" in output


def test_cmd_sample_down_reports_missing_generated_runtime(capsys, monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_sample_down_reports_missing_generated_runtime` 시나리오를 검증한다.

    주요 흐름은 `type()`, `type('Args', (), {'volumes': False})()`, `cmd_sample_down()`, `readouterr()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        capsys: capsys과(와) 관련된 입력값이다.
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    monkeypatch.setattr(specyn, "SAMPLE_COMPOSE_FILE", tmp_path / "projects" / "sample-service" / "docker-compose.local.yml")

    args = type("Args", (), {
        "volumes": False,
    })()

    exit_code = specyn.cmd_sample_down(args)
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "SAMPLE_RUNTIME_NOT_GENERATED" in output


def test_cmd_setup_writes_env_when_docker_daemon_is_unavailable(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_setup_writes_env_when_docker_daemon_is_unavailable` 시나리오를 검증한다.

    주요 흐름은 `type()`, `type('Args', (), {'auth_mode': 'openapi', 'model': 'gpt-5.4', 'api_key': 'sk-test-1234', 'chatgpt_action': None, 'install_codex': 'auto', 'non_interactive': True, 'browser_login': False})()`, `cmd_setup()`, `readouterr()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    env_file = tmp_path / ".env"
    env_example = tmp_path / ".env.example"
    env_example.write_text("SPECYN_AUTH_MODE=chatgpt\nOPENAI_MODEL=gpt-5.4\n", encoding="utf-8")

    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(specyn, "ENV_FILE", env_file)
    monkeypatch.setattr(specyn, "ENV_EXAMPLE_FILE", env_example)
    monkeypatch.setattr(specyn, "CODEX_HOME_DIR", tmp_path / ".specyn" / "codex")
    monkeypatch.setattr(specyn, "CODEX_AUTH_FILE", tmp_path / ".specyn" / "codex" / "auth.json")
    compose_file = tmp_path / "docker-compose.local.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setattr(specyn, "DASHBOARD_COMPOSE_FILE", compose_file)
    monkeypatch.setattr(specyn.shutil, "which", lambda binary: "/usr/bin/docker" if binary == "docker" else None)
    monkeypatch.setattr(
        specyn,
        "docker_daemon_status",
        lambda: (False, "failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine"),
    )

    args = type("Args", (), {
        "auth_mode": "openapi",
        "model": "gpt-5.4",
        "api_key": "sk-test-1234",
        "chatgpt_action": None,
        "install_codex": "auto",
        "non_interactive": True,
        "browser_login": False,
    })()

    exit_code = specyn.cmd_setup(args)
    output = json.loads(capsys.readouterr().out)
    env_text = env_file.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "OPENAI_API_KEY=sk-test-1234" in env_text
    assert output["dockerDaemonReady"] is False
    assert output["dockerVerificationAttempted"] is False
    assert output["dockerAuthApplied"] is False
    assert output["warnings"]
