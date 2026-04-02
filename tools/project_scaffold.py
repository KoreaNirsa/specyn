"""
새 프로젝트가 실행 가능한 최소 런타임 구조를 갖추도록 기본 디렉터리와 파일 골격을 만들어 주는 스캐폴드 생성 모듈이다.
백엔드, AI 서버, 프런트엔드, 문서, compose 설정을 프로젝트 ID 기준으로 한 번에 준비해 이후 생성 단계가 파일 부재 때문에 실패하지 않게 한다.
"""

from __future__ import annotations

from pathlib import Path
import shutil
from textwrap import dedent

from tools.code_comments import annotate_source, should_annotate_path


SAMPLE_FRONTEND_PORT = 5173
SAMPLE_BACKEND_PORT = 8080
SAMPLE_AI_SERVER_PORT = 8000


def ensure_project_runtime_scaffold(*, project_id: str, output_root: Path, repo_root: Path) -> list[str]:
    """
    도구 계층에서 프로젝트 런타임 스캐폴드이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_ensure_backend_scaffold()`, `_ensure_ai_server_scaffold()`, `_ensure_frontend_scaffold()`, `_ensure_docs_scaffold()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.
        repo_root: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    created_files: list[str] = []

    created_files.extend(_ensure_backend_scaffold(project_id=project_id, output_root=output_root, repo_root=repo_root))
    created_files.extend(_ensure_ai_server_scaffold(project_id=project_id, output_root=output_root, repo_root=repo_root))
    created_files.extend(_ensure_frontend_scaffold(project_id=project_id, output_root=output_root))
    created_files.extend(_ensure_docs_scaffold(project_id=project_id, output_root=output_root))
    created_files.extend(_ensure_project_root_files(project_id=project_id, output_root=output_root))

    return created_files


def _ensure_backend_scaffold(*, project_id: str, output_root: Path, repo_root: Path) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, 백엔드 스캐폴드이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_copy_tree_if_missing()`, `annotate_source()`, `_build_backend_application_yml()`, `_build_backend_readme()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.
        repo_root: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    source_root = repo_root / "dashboard" / "backend"
    target_root = output_root / "backend"
    created_files = _copy_tree_if_missing(
        source_root,
        target_root,
        skip_relative_paths={Path("src/main/resources/application.yml")},
    )

    application_yml = target_root / "src" / "main" / "resources" / "application.yml"
    if not application_yml.exists():
        application_yml.parent.mkdir(parents=True, exist_ok=True)
        application_yml.write_text(annotate_source(application_yml, _build_backend_application_yml(project_id)), encoding="utf-8")
        created_files.append(str(application_yml))

    readme_path = target_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(annotate_source(readme_path, _build_backend_readme(project_id)), encoding="utf-8")
        created_files.append(str(readme_path))

    return created_files


def _ensure_ai_server_scaffold(*, project_id: str, output_root: Path, repo_root: Path) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, AI server 스캐폴드이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_copy_tree_if_missing()`, `annotate_source()`, `_build_ai_server_config()`, `_build_ai_server_health_test()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.
        repo_root: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    source_root = repo_root / "dashboard" / "ai-server"
    target_root = output_root / "ai-server"
    created_files = _copy_tree_if_missing(
        source_root,
        target_root,
        skip_relative_paths={
            Path("app/core/config.py"),
            Path("tests/test_health.py"),
            Path("tests/test_prompt_builder.py"),
            Path("tests/test_rag_service.py"),
        },
    )

    ai_config_path = target_root / "app" / "core" / "config.py"
    if not ai_config_path.exists():
        ai_config_path.parent.mkdir(parents=True, exist_ok=True)
        ai_config_path.write_text(annotate_source(ai_config_path, _build_ai_server_config()), encoding="utf-8")
        created_files.append(str(ai_config_path))

    for path, content in {
        target_root / "tests" / "test_health.py": _build_ai_server_health_test(),
        target_root / "tests" / "test_prompt_builder.py": _build_ai_server_prompt_builder_test(project_id),
        target_root / "tests" / "test_rag_service.py": _build_ai_server_rag_service_test(),
    }.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(annotate_source(path, content), encoding="utf-8")
        created_files.append(str(path))

    readme_path = target_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(annotate_source(readme_path, _build_ai_server_readme(project_id)), encoding="utf-8")
        created_files.append(str(readme_path))

    return created_files


def _ensure_frontend_scaffold(*, project_id: str, output_root: Path) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 스캐폴드이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_build_frontend_package_json()`, `_build_frontend_tsconfig()`, `_build_frontend_vite_config()`, `_build_frontend_index_html()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    target_root = output_root / "frontend"
    files = {
        target_root / "package.json": _build_frontend_package_json(project_id),
        target_root / "tsconfig.json": _build_frontend_tsconfig(),
        target_root / "vite.config.ts": _build_frontend_vite_config(),
        target_root / "index.html": _build_frontend_index_html(project_id),
        target_root / "src" / "App.tsx": _build_frontend_app(project_id),
        target_root / "src" / "main.tsx": _build_frontend_main(),
        target_root / "src" / "styles.css": _build_frontend_styles(),
        target_root / "src" / "vite-env.d.ts": _build_frontend_vite_env(),
        target_root / "README.md": _build_frontend_readme(project_id),
    }

    created_files: list[str] = []
    for path, content in files.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(annotate_source(path, content), encoding="utf-8")
        created_files.append(str(path))
    return created_files


def _ensure_docs_scaffold(*, project_id: str, output_root: Path) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, 문서 집합 스캐폴드이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_build_docs_readme()`, `annotate_source()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    docs_root = output_root / "docs"
    created_files: list[str] = []
    for path, content in {
        docs_root / "README.md": _build_docs_readme(project_id),
        docs_root / "generated" / ".gitkeep": "",
        docs_root / "openapi" / ".gitkeep": "",
    }.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(annotate_source(path, content), encoding="utf-8")
        created_files.append(str(path))
    return created_files


def _ensure_project_root_files(*, project_id: str, output_root: Path) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, 프로젝트 root 파일 목록이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `_build_project_readme()`, `_build_project_compose()`, `annotate_source()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        output_root: 산출물을 기록할 기준 루트 경로다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    created_files: list[str] = []
    files = {
        output_root / "README.md": _build_project_readme(project_id),
        output_root / "docker-compose.local.yml": _build_project_compose(project_id),
    }
    for path, content in files.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(annotate_source(path, content), encoding="utf-8")
        created_files.append(str(path))
    return created_files


def _copy_tree_if_missing(source_root: Path, target_root: Path, *, skip_relative_paths: set[Path] | None = None) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, `copy_tree_if_missing()`가 맡는 트리 if missing 관련 작업을 수행한다.

    주요 흐름은 `rglob()`, `is_dir()`, `should_annotate_path()`, `annotate_source()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        source_root: 파일 시스템 경로 객체다.
        target_root: 파일 시스템 경로 객체다.
        skip_relative_paths: skip relative 경로 목록을(를) 나타내는 `set[Path] | None` 타입 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    if not source_root.exists():
        return []

    ignored_paths = skip_relative_paths or set()
    created_files: list[str] = []
    for source_path in sorted(source_root.rglob("*")):
        relative_path = source_path.relative_to(source_root)
        if relative_path in ignored_paths:
            continue
        target_path = target_root / relative_path
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue
        if target_path.exists():
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if should_annotate_path(target_path):
            target_path.write_text(annotate_source(target_path, source_path.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(source_path, target_path)
        created_files.append(str(target_path))
    return created_files


def _build_backend_application_yml(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 백엔드 application yml을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        spring:
          application:
            name: {project_id}-backend
          threads:
            virtual:
              enabled: true

        server:
          port: ${{SERVER_PORT:{SAMPLE_BACKEND_PORT}}}

        management:
          endpoints:
            web:
              exposure:
                include: health,info

        axbuilder:
          ai:
            base-url: ${{AI_SERVER_URL:http://localhost:{SAMPLE_AI_SERVER_PORT}}}
            timeout-seconds: 120
          security:
            enabled: ${{AXB_SECURITY_ENABLED:false}}
          cors:
            allowed-origins: ${{AXB_CORS_ALLOWED_ORIGINS:http://localhost:{SAMPLE_FRONTEND_PORT},http://127.0.0.1:{SAMPLE_FRONTEND_PORT}}}
        """
    ).strip() + "\n"


def _build_ai_server_config() -> str:
    """
    모듈 내부 전용 헬퍼로, AI server 설정을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        from functools import lru_cache
        from pathlib import Path

        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            specyn_auth_mode: str = "chatgpt"
            openai_api_key: str | None = None
            openai_base_url: str = "https://api.openai.com/v1"
            openai_model: str = "gpt-5.4"
            codex_model: str = "gpt-5.4"
            codex_exec_mode: str = "cli"
            codex_command_template: str = "codex exec --json --model {{model}} -C {{workspace}} --skip-git-repo-check"
            codex_home: str = ".specyn/codex"
            codex_timeout_seconds: int = 900
            rag_docs_dir: str = "docs"
            rag_chunk_size: int = 1200
            rag_chunk_overlap: int = 120
            prompt_snapshot_dir: str = ".specyn/prompts"
            axb_cors_allowed_origins: str = "http://localhost:{SAMPLE_FRONTEND_PORT},http://127.0.0.1:{SAMPLE_FRONTEND_PORT}"

            model_config = SettingsConfigDict(
                env_file=".env",
                env_file_encoding="utf-8",
                extra="ignore",
            )

            @property
            def project_root(self) -> Path:
                return Path(__file__).resolve().parents[3]

            @property
            def cors_allowed_origins(self) -> list[str]:
                return [
                    origin.strip()
                    for origin in self.axb_cors_allowed_origins.split(",")
                    if origin.strip()
                ]


        @lru_cache
        def get_settings() -> Settings:
            return Settings()
        """
    ).strip() + "\n"


def _build_frontend_package_json(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 package JSON을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        {{
          "name": "specyn-{project_id}-frontend",
          "private": true,
          "version": "0.1.0",
          "type": "module",
          "engines": {{
            "node": ">=20.19.0"
          }},
          "scripts": {{
            "dev": "vite",
            "build": "tsc --noEmit && vite build",
            "typecheck": "tsc --noEmit",
            "preview": "vite preview"
          }},
          "dependencies": {{
            "react": "19.2.4",
            "react-dom": "19.2.4"
          }},
          "devDependencies": {{
            "@types/react": "19.2.2",
            "@types/react-dom": "19.2.2",
            "@vitejs/plugin-react": "6.0.1",
            "typescript": "6.0.2",
            "vite": "8.0.3"
          }}
        }}
        """
    ).strip() + "\n"


def _build_frontend_tsconfig() -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 tsconfig을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        """
        {
          "compilerOptions": {
            "target": "ES2022",
            "useDefineForClassFields": true,
            "lib": ["ES2022", "DOM", "DOM.Iterable"],
            "allowJs": false,
            "skipLibCheck": true,
            "esModuleInterop": true,
            "allowSyntheticDefaultImports": true,
            "strict": true,
            "forceConsistentCasingInFileNames": true,
            "module": "ESNext",
            "moduleResolution": "Bundler",
            "resolveJsonModule": true,
            "isolatedModules": true,
            "noEmit": true,
            "jsx": "react-jsx"
          },
          "include": ["src"],
          "references": []
        }
        """
    ).strip() + "\n"


def _build_frontend_vite_config() -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 vite 설정을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        import {{ defineConfig }} from "vite";
        import react from "@vitejs/plugin-react";

        export default defineConfig({{
          plugins: [react()],
          server: {{
            port: {SAMPLE_FRONTEND_PORT},
            host: "0.0.0.0",
          }},
        }});
        """
    ).strip() + "\n"


def _build_frontend_index_html(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 index html을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        <!doctype html>
        <html lang="ko">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{project_id}</title>
          </head>
          <body>
            <div id="root"></div>
            <script type="module" src="/src/main.tsx"></script>
          </body>
        </html>
        """
    ).strip() + "\n"


def _build_frontend_app(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 애플리케이션을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        import GeneratedProjectPage from "./generated/{project_id}/GeneratedProjectPage";

        export default function App() {{
          return (
            <div className="layout">
              <header className="topbar">
                <div>
                  <p className="eyebrow">Generated Project Runtime</p>
                  <h1>{project_id}</h1>
                  <p className="muted-text">
                    Specyn 대시보드와 분리된 실제 프로젝트 런타임입니다. frontend/backend/ai-server 가
                    projects/{project_id} 아래에 독립 배치되어 있습니다.
                  </p>
                </div>
                <div className="button-row">
                  <a
                    className="link-button"
                    href="http://localhost:{SAMPLE_BACKEND_PORT}/api/v1/generated/{project_id}/summary"
                    rel="noreferrer"
                    target="_blank"
                  >
                    Backend Summary
                  </a>
                  <a
                    className="link-button secondary-link-button"
                    href="http://localhost:{SAMPLE_AI_SERVER_PORT}/generated/{project_id}/context"
                    rel="noreferrer"
                    target="_blank"
                  >
                    AI Context
                  </a>
                </div>
              </header>
              <GeneratedProjectPage />
            </div>
          );
        }}
        """
    ).strip() + "\n"


def _build_frontend_main() -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 메인 진입점을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        """
        import React from "react";
        import ReactDOM from "react-dom/client";

        import App from "./App";
        import "./styles.css";

        ReactDOM.createRoot(document.getElementById("root")!).render(
          <React.StrictMode>
            <App />
          </React.StrictMode>,
        );
        """
    ).strip() + "\n"


def _build_frontend_styles() -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 styles을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        """
        :root {
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color-scheme: dark;
          background: #09111b;
          color: #e8eef7;
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: radial-gradient(circle at top right, rgba(0, 229, 255, 0.10), transparent 24%), #09111b; }
        .layout { max-width: 1240px; margin: 0 auto; padding: 32px 24px 56px; }
        .topbar { display: flex; justify-content: space-between; gap: 24px; align-items: flex-start; margin-bottom: 24px; padding: 28px; border-radius: 24px; background: rgba(14, 20, 29, 0.92); border: 1px solid rgba(255,255,255,0.08); }
        .eyebrow { margin: 0 0 8px; color: #8ea0b8; font-size: 0.8rem; letter-spacing: 0.16em; text-transform: uppercase; }
        h1 { margin: 0 0 10px; font-size: 2rem; }
        .muted-text { margin: 0; color: #b5c2d3; line-height: 1.6; max-width: 720px; }
        .button-row { display: flex; flex-wrap: wrap; gap: 12px; }
        .link-button { display: inline-flex; align-items: center; justify-content: center; padding: 12px 18px; border-radius: 14px; text-decoration: none; background: linear-gradient(135deg, #6be9ff, #11d8f5); color: #081018; font-weight: 700; }
        .secondary-link-button { background: rgba(255,255,255,0.06); color: #ebf3ff; border: 1px solid rgba(255,255,255,0.1); }
        @media (max-width: 960px) { .topbar { flex-direction: column; } }
        """
    ).strip() + "\n"


def _build_frontend_vite_env() -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 vite 환경 변수을(를) 조립하거나 생성한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return "/// <reference types=\"vite/client\" />\n"


def _build_project_compose(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프로젝트 Compose 설정을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        services:
          ai-server:
            build:
              context: ../../
              dockerfile: docker/ai-server.Dockerfile
            working_dir: /workspace
            env_file:
              - ../../.env
            environment:
              CODEX_HOME: /workspace/.specyn/codex
            volumes:
              - ../../:/workspace
            command:
              [
                "bash",
                "-lc",
                "python -m uvicorn app.main:app --app-dir projects/{project_id}/ai-server --host 0.0.0.0 --port {SAMPLE_AI_SERVER_PORT} --reload",
              ]
            ports:
              - "{SAMPLE_AI_SERVER_PORT}:{SAMPLE_AI_SERVER_PORT}"

          backend:
            image: gradle:8.14.0-jdk21
            working_dir: /workspace/projects/{project_id}/backend
            env_file:
              - ../../.env
            volumes:
              - ../../:/workspace
            command: ["gradle", "--no-daemon", "bootRun"]
            environment:
              AI_SERVER_URL: http://ai-server:{SAMPLE_AI_SERVER_PORT}
            ports:
              - "{SAMPLE_BACKEND_PORT}:{SAMPLE_BACKEND_PORT}"
            depends_on:
              - ai-server

          frontend:
            image: node:20-bookworm
            working_dir: /workspace/projects/{project_id}/frontend
            env_file:
              - ../../.env
            volumes:
              - ../../:/workspace
            command: ["sh", "-lc", "npm install && npm run dev -- --host 0.0.0.0 --port {SAMPLE_FRONTEND_PORT}"]
            ports:
              - "{SAMPLE_FRONTEND_PORT}:{SAMPLE_FRONTEND_PORT}"
            depends_on:
              - backend
        """
    ).strip() + "\n"


def _build_project_readme(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프로젝트 readme을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        # {project_id}

        이 디렉터리는 `python specyn.py run --spec-dir specs/projects/{project_id} --project-id {project_id}` 실행으로
        생성되는 실제 프로젝트 런타임입니다.

        ## 실행 포트
        - Frontend: http://localhost:{SAMPLE_FRONTEND_PORT}
        - Backend: http://localhost:{SAMPLE_BACKEND_PORT}
        - AI Server: http://localhost:{SAMPLE_AI_SERVER_PORT}
        """
    ).strip() + "\n"


def _build_backend_readme(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 백엔드 readme을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        # {project_id} backend

        Specyn이 생성한 API와 컨트롤러를 실행하는 Spring Boot 런타임입니다.
        기본 포트는 `{SAMPLE_BACKEND_PORT}` 입니다.
        """
    ).strip() + "\n"


def _build_ai_server_readme(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, AI server readme을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        # {project_id} ai-server

        Specyn이 생성한 context route와 prompt 관련 기능을 실행하는 FastAPI 런타임입니다.
        기본 포트는 `{SAMPLE_AI_SERVER_PORT}` 입니다.
        """
    ).strip() + "\n"


def _build_frontend_readme(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 프런트엔드 readme을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        # {project_id} frontend

        Specyn이 생성한 `GeneratedProjectPage.tsx` 를 표시하는 Vite + React 런타임입니다.
        기본 포트는 `{SAMPLE_FRONTEND_PORT}` 입니다.
        """
    ).strip() + "\n"


def _build_docs_readme(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, 문서 집합 readme을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        # {project_id} docs

        `generated/` 와 `openapi/` 아래 문서는 `specyn.py run` 이 갱신합니다.
        """
    ).strip() + "\n"


def _build_ai_server_health_test() -> str:
    """
    모듈 내부 전용 헬퍼로, AI server 헬스체크 테스트을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        import pathlib
        import sys

        from fastapi.testclient import TestClient

        ROOT = pathlib.Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(ROOT / "ai-server"))

        from app.main import app  # noqa: E402


        client = TestClient(app)


        def test_health() -> None:
            response = client.get("/health")
            assert response.status_code == 200
            payload = response.json()
            assert payload["status"] == "UP"
            assert payload["service"] == "ai-server"


        def test_health_allows_frontend_origin_via_cors() -> None:
            response = client.get("/health", headers={{"Origin": "http://localhost:{SAMPLE_FRONTEND_PORT}"}})

            assert response.status_code == 200
            assert response.headers["access-control-allow-origin"] == "http://localhost:{SAMPLE_FRONTEND_PORT}"
        """
    ).strip() + "\n"


def _build_ai_server_prompt_builder_test(project_id: str) -> str:
    """
    모듈 내부 전용 헬퍼로, AI server 프롬프트 builder 테스트을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        f"""
        import pathlib
        import sys

        ROOT = pathlib.Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(ROOT / "ai-server"))

        from app.models.contracts import AgentExecutionRequest, SpecDocument  # noqa: E402
        from app.services.prompt_builder import PromptBuilder  # noqa: E402


        def test_prompt_builder_contains_spec_bundle() -> None:
            request = AgentExecutionRequest(
                agent="API",
                projectId="{project_id}",
                documents=[
                    SpecDocument(
                        name="api.md",
                        type="api",
                        content="# 목적\\nTask CRUD API 생성",
                    )
                ],
                previousResults=[],
                workspacePath=".workspace/{project_id}",
                dryRun=True,
            )

            prompt = PromptBuilder().build(request)

            assert "프로젝트 ID: {project_id}" in prompt
            assert "에이전트: api" in prompt
            assert '<spec name="api.md" type="api">' in prompt
            assert "Task CRUD API 생성" in prompt
            assert "프롬프트 안전 가드레일" in prompt
            assert "필수 출력 계약" in prompt
        """
    ).strip() + "\n"


def _build_ai_server_rag_service_test() -> str:
    """
    모듈 내부 전용 헬퍼로, AI server RAG 서비스 테스트을(를) 조립하거나 생성한다.

    주요 흐름은 `dedent()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return dedent(
        """
        import asyncio
        import pathlib
        import sys

        ROOT = pathlib.Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(ROOT / "ai-server"))

        from app.services.rag_service import RagService  # noqa: E402


        def test_rag_service_returns_items() -> None:
            service = RagService()
            response = asyncio.run(service.search("spec validation", 3))
            assert len(response.items) > 0


        def test_should_use_langchain_runtime_disabled_on_python_314() -> None:
            from app.services.rag_service import should_use_langchain_runtime

            assert should_use_langchain_runtime((3, 13)) is True
            assert should_use_langchain_runtime((3, 14)) is False
        """
    ).strip() + "\n"
