from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable

import yaml

from tools.agent_flow import ExecutionStep, build_execution_plan
from tools.prompt_compiler import compile_prompt
from tools.spec_blueprint import ApiEndpoint, ProjectBlueprint, blueprint_to_manifest, build_project_blueprint
from tools.spec_loader import SpecDocument

ROOT_DIR = Path(__file__).resolve().parents[1]
PROMPT_ROOT_DIR = ROOT_DIR / ".specyn" / "prompts"
GENERATED_DOCS_DIR = ROOT_DIR / "docs" / "generated"
GENERATED_AI_SERVER_DIR = ROOT_DIR / "ai-server" / "app" / "generated"


@dataclass(slots=True)
class StepExecutionResult:
    agent: str
    status: str
    summary: str
    generated_files: list[str]
    validations: list[str]


@dataclass(slots=True)
class LocalRunResult:
    run_id: str
    status: str
    results: list[StepExecutionResult]
    generated_files: list[str]
    prompt_dir: Path
    workspace_dir: Path


Generator = Callable[[ProjectBlueprint, Path], dict[Path, str]]


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


class LocalSddRuntime:
    def __init__(self, *, output_root: Path | None = None) -> None:
        self.output_root = (output_root or ROOT_DIR).resolve()

    def execute(
        self,
        *,
        project_id: str,
        bundle: dict[str, SpecDocument],
        workspace_path: str,
        rag_enabled: bool,
        runtime_mode: str,
    ) -> LocalRunResult:
        blueprint = build_project_blueprint(
            project_id=project_id,
            bundle=bundle,
            rag_enabled=rag_enabled,
        )
        workspace_dir = self._resolve_workspace_path(workspace_path)
        prompt_dir = PROMPT_ROOT_DIR / blueprint.slug
        prompt_dir.mkdir(parents=True, exist_ok=True)

        run_id = datetime.now(UTC).strftime(f"{blueprint.slug}-%Y%m%dT%H%M%SZ")
        run_root = workspace_dir / ".specyn" / "runs" / run_id
        reports_dir = run_root / "steps"
        reports_dir.mkdir(parents=True, exist_ok=True)

        execution_plan = build_execution_plan(bundle, rag_enabled=rag_enabled)
        previous_outputs: list[str] = []
        results: list[StepExecutionResult] = []
        all_generated_files: list[str] = []

        generators = self._build_generators()

        for step in execution_plan:
            prompt = compile_prompt(
                agent_name=step.agent,
                bundle=bundle,
                previous_outputs=previous_outputs,
                workspace_path=str(workspace_dir),
            )
            prompt_path = prompt_dir / f"{step.label}.prompt.md"
            self._write_file(prompt_path, prompt)

            generated_files: list[str] = []
            validations = [
                "spec bundle 검증 통과",
                f"phase={step.phase}",
                f"feedbackRound={step.round_number}",
                f"prompt={prompt_path.relative_to(self.output_root)}",
            ]

            if runtime_mode == "simulate":
                status = "SIMULATED"
                summary = (
                    f"[simulate] {step.agent} 단계는 prompt만 생성했습니다. "
                    f"project={blueprint.slug} step={step.label}"
                )
                validations.append("runtime=simulate")
            else:
                status, summary, generated_files = self._execute_step(
                    step=step,
                    blueprint=blueprint,
                    generator=generators.get(step.agent),
                )
                validations.append("runtime=local")
                if generated_files:
                    validations.append(f"generatedFiles={len(generated_files)}")
                    all_generated_files.extend(generated_files)

            report_path = reports_dir / f"{step.label}.md"
            report = self._build_step_report(
                step=step,
                status=status,
                summary=summary,
                generated_files=generated_files,
                validations=validations,
            )
            self._write_file(report_path, report)
            validations.append(f"report={report_path.relative_to(self.output_root)}")

            results.append(
                StepExecutionResult(
                    agent=step.agent.upper().replace("-", "_"),
                    status=status,
                    summary=summary,
                    generated_files=generated_files,
                    validations=validations,
                )
            )
            previous_outputs.append(summary)

        manifest_path = run_root / "manifest.json"
        manifest = {
            "runId": run_id,
            "projectId": blueprint.slug,
            "runtimeMode": runtime_mode,
            "generatedFiles": all_generated_files,
            "results": [
                {
                    "agent": result.agent,
                    "status": result.status,
                    "summary": result.summary,
                    "generatedFiles": result.generated_files,
                    "validations": result.validations,
                }
                for result in results
            ],
            "blueprint": blueprint_to_manifest(blueprint),
        }
        self._write_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

        return LocalRunResult(
            run_id=run_id,
            status="SIMULATED" if runtime_mode == "simulate" else "COMPLETED",
            results=results,
            generated_files=all_generated_files,
            prompt_dir=prompt_dir,
            workspace_dir=workspace_dir,
        )

    def _resolve_workspace_path(self, workspace_path: str) -> Path:
        path = Path(workspace_path)
        if not path.is_absolute():
            path = self.output_root / path
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _execute_step(
        self,
        *,
        step: ExecutionStep,
        blueprint: ProjectBlueprint,
        generator: Generator | None,
    ) -> tuple[str, str, list[str]]:
        if step.phase != "main":
            summary = (
                f"[feedback] {step.agent} 단계는 {step.phase} round={step.round_number} 기준으로 "
                f"기존 산출물을 재검토했습니다. 추가 파일 변경은 없으며 handoff만 갱신했습니다."
            )
            return "COMPLETED", summary, []

        if generator is None:
            return "COMPLETED", self._non_generating_summary(step.agent, blueprint), []

        file_map = generator(blueprint, self.output_root)
        generated_files: list[str] = []
        for path, content in file_map.items():
            self._write_file(path, content)
            generated_files.append(str(path.relative_to(self.output_root)))

        return "COMPLETED", self._generating_summary(step.agent, blueprint, generated_files), generated_files

    def _write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _non_generating_summary(self, agent_name: str, blueprint: ProjectBlueprint) -> str:
        summaries = {
            "planner": f"{blueprint.title} 프로젝트의 목적, 시나리오, NFR을 실행 계획으로 정규화했습니다.",
            "design": f"{blueprint.title} UI 흐름과 상태 전이를 정리했습니다.",
            "rag": f"{blueprint.title} 관련 내부 문서 검색 후보를 정리했습니다.",
            "code-analysis": "생성된 산출물의 구조 일관성과 결합도를 점검했습니다.",
            "security": "입력 검증, 민감 정보 노출, 안전한 기본값 관점의 리뷰를 남겼습니다.",
            "performance": "핵심 요청 경로와 병목 후보를 기준으로 성능 관점을 점검했습니다.",
            "review": "구조/보안/테스트/운영 기준으로 release readiness를 검토했습니다.",
            "final-review": "전체 SDD run 결과를 종합해 최종 handoff 상태를 정리했습니다.",
        }
        return summaries.get(agent_name, f"{agent_name} 단계 검토를 완료했습니다.")

    def _generating_summary(self, agent_name: str, blueprint: ProjectBlueprint, generated_files: list[str]) -> str:
        summaries = {
            "api": f"OpenAPI 계약과 프런트/백엔드 공용 API contract를 생성했습니다. endpoints={len(self._effective_endpoints(blueprint))}",
            "backend": "Spring Boot controller와 AI Server generated router를 생성했습니다.",
            "frontend": "Vite UI에서 바로 확인 가능한 generated project page를 생성했습니다.",
            "dba": "DDL 초안과 저장 전략 메모를 생성했습니다.",
            "devops": "로컬 실행용 compose/env 계약 초안을 생성했습니다.",
            "test": "자동화 확인용 generated smoke test와 테스트 계획을 생성했습니다.",
            "docs": "프로젝트 README와 실행 가이드를 생성했습니다.",
        }
        if blueprint.slug == "sample-service":
            summaries["backend"] = "샘플 Task CRUD demo를 위한 Spring Boot controller와 AI Server generated router를 생성했습니다."
            summaries["frontend"] = "목록/생성/상태 변경/삭제를 바로 확인할 수 있는 sample-service CRUD 페이지를 생성했습니다."
            summaries["dba"] = "sample-service CRUD 흐름에 맞춘 테이블 DDL 초안을 생성했습니다."
            summaries["docs"] = "sample-service 실행 확인 절차를 포함한 프로젝트 문서를 생성했습니다."
        return summaries.get(agent_name, f"{agent_name} 산출물을 생성했습니다.") + f" files={len(generated_files)}"

    def _build_step_report(
        self,
        *,
        step: ExecutionStep,
        status: str,
        summary: str,
        generated_files: list[str],
        validations: list[str],
    ) -> str:
        changed_files = ", ".join(generated_files) if generated_files else "none"
        validation_block = "\n".join(f"- {item}" for item in validations)
        return dedent(
            f"""
            STEP_LABEL: {step.label}
            AGENT: {step.agent}
            PHASE: {step.phase}
            FEEDBACK_ROUND: {step.round_number}
            STATUS: {status.lower()}
            CHANGED_FILES: {changed_files}
            RESOLVED: {summary}
            UNRESOLVED: none
            BLOCKERS: none
            NEXT_HANDOFF: 다음 agent가 prompt와 manifest를 함께 확인합니다.

            # 작업 요약
            {summary}

            # Validation
            {validation_block}
            """
        ).strip() + "\n"

    def _build_generators(self) -> dict[str, Generator]:
        return {
            "api": self._generate_api_outputs,
            "backend": self._generate_backend_outputs,
            "frontend": self._generate_frontend_outputs,
            "dba": self._generate_dba_outputs,
            "devops": self._generate_devops_outputs,
            "test": self._generate_test_outputs,
            "docs": self._generate_docs_outputs,
        }

    def _effective_endpoints(self, blueprint: ProjectBlueprint) -> tuple[ApiEndpoint, ...]:
        if blueprint.endpoints:
            return blueprint.endpoints
        return (
            ApiEndpoint(
                method="GET",
                path=f"/api/v1/{blueprint.slug}/summary",
                description=f"{blueprint.title} summary",
                auth="없음",
                note="auto-generated fallback endpoint",
                operation_id="get_summary",
                java_method_name="getSummary",
                ts_method_name="get_summary",
                path_variables=tuple(),
                response_status=200,
                request_body_allowed=False,
            ),
        )

    def _generate_api_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        frontend_dir = self.output_root / "frontend" / "src" / "generated" / blueprint.slug
        return {
            self.output_root / "docs" / "openapi" / f"{blueprint.slug}.yaml": self._build_openapi_yaml(blueprint),
            frontend_dir / "apiContract.ts": self._build_frontend_api_contract(blueprint),
        }

    def _generate_backend_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        java_dir = self.output_root / "backend" / "src" / "main" / "java" / "com" / "axbuilder" / "backend" / "generated" / blueprint.package_slug
        ai_server_dir = GENERATED_AI_SERVER_DIR / blueprint.package_slug
        return {
            java_dir / f"Generated{blueprint.class_name}Controller.java": self._build_backend_controller(blueprint),
            GENERATED_AI_SERVER_DIR / "__init__.py": '"""Runtime-generated AI server modules."""\n',
            ai_server_dir / "__init__.py": f'"""Generated routes for {blueprint.slug}."""\n',
            ai_server_dir / "router.py": self._build_ai_server_router(blueprint),
        }

    def _generate_frontend_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        frontend_dir = self.output_root / "frontend" / "src" / "generated" / blueprint.slug
        return {frontend_dir / "GeneratedProjectPage.tsx": self._build_frontend_page(blueprint)}

    def _generate_dba_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        return {
            self.output_root / "backend" / "src" / "main" / "resources" / "db" / "generated" / f"{blueprint.slug}.sql": self._build_sql_blueprint(blueprint)
        }

    def _generate_devops_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        return {
            self.output_root / ".specyn" / "generated" / blueprint.slug / "docker-compose.generated.yml": self._build_generated_compose(blueprint)
        }

    def _generate_test_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        return {
            self.output_root / "ai-server" / "tests" / "generated" / f"test_{blueprint.package_slug}_generated_route.py": self._build_ai_server_test(blueprint),
            GENERATED_DOCS_DIR / f"{blueprint.slug}-test-plan.md": self._build_test_plan(blueprint),
        }

    def _generate_docs_outputs(self, blueprint: ProjectBlueprint, _: Path) -> dict[Path, str]:
        return {GENERATED_DOCS_DIR / f"{blueprint.slug}.md": self._build_project_doc(blueprint)}

    def _build_openapi_yaml(self, blueprint: ProjectBlueprint) -> str:
        document: dict[str, Any] = {
            "openapi": "3.1.0",
            "info": {
                "title": f"{blueprint.title} Generated API",
                "version": "1.0.0",
                "description": blueprint.summary,
            },
            "servers": [{"url": "http://localhost:8080"}],
            "paths": {},
            "x-specyn": {
                "executionFlow": list(blueprint.execution_flow) or ["planner"],
                "errorPolicies": list(blueprint.error_policies) or ["none"],
            },
        }

        paths = document["paths"]
        assert isinstance(paths, dict)
        for endpoint in self._effective_endpoints(blueprint):
            path_item = paths.setdefault(endpoint.path, {})
            assert isinstance(path_item, dict)
            operation: dict[str, Any] = {
                "operationId": endpoint.operation_id,
                "summary": endpoint.description,
                "tags": [blueprint.slug],
                "responses": {
                    str(endpoint.response_status): self._openapi_response(blueprint, endpoint),
                },
            }
            request_example = self._openapi_request_example(blueprint, endpoint)
            if endpoint.request_body_allowed and request_example is not None:
                operation["requestBody"] = {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"},
                            "example": request_example,
                        }
                    },
                }
            path_item[endpoint.method.lower()] = operation

        return yaml.dump(
            document,
            Dumper=NoAliasSafeDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    def _openapi_request_example(self, blueprint: ProjectBlueprint, endpoint: ApiEndpoint) -> dict[str, Any] | None:
        if endpoint.method == "PATCH" and endpoint.path.endswith("/status"):
            return {"status": "DONE"}
        if endpoint.request_body_allowed:
            return blueprint.request_example or {"sample": "value"}
        return None

    def _openapi_response(self, blueprint: ProjectBlueprint, endpoint: ApiEndpoint) -> dict[str, Any]:
        response: dict[str, Any] = {"description": endpoint.description}
        if endpoint.response_status == 204:
            return response

        response["content"] = {
            "application/json": {
                "schema": {"type": "object"},
                "example": self._openapi_response_example(blueprint, endpoint),
            }
        }
        return response

    def _openapi_response_example(self, blueprint: ProjectBlueprint, endpoint: ApiEndpoint) -> dict[str, Any]:
        base_item = self._openapi_base_item_example(blueprint)
        if blueprint.slug == "sample-service":
            if endpoint.method == "GET" and endpoint.path == "/api/v1/tasks":
                return {"items": [base_item], "count": 1}
            if endpoint.method == "GET" and endpoint.path.endswith("/{id}"):
                return {"item": base_item}
            if endpoint.method == "POST":
                return {"item": base_item, "count": 3}
            if endpoint.method == "PATCH" and endpoint.path.endswith("/status"):
                return {"item": dict(base_item, status="DONE")}
        return blueprint.response_example or {"status": "ok"}

    def _openapi_base_item_example(self, blueprint: ProjectBlueprint) -> dict[str, Any]:
        response_example = blueprint.response_example or {}
        item = response_example.get("item") if isinstance(response_example, dict) else None
        if isinstance(item, dict):
            return item
        items = response_example.get("items") if isinstance(response_example, dict) else None
        if isinstance(items, list) and items and isinstance(items[0], dict):
            return items[0]
        if isinstance(response_example, dict) and response_example:
            return response_example
        return {"status": "ok"}

    def _build_frontend_api_contract(self, blueprint: ProjectBlueprint) -> str:
        manifest_text = json.dumps(blueprint_to_manifest(blueprint), ensure_ascii=False, indent=2)
        return dedent(
            f"""
            export const generatedApiContract = {manifest_text} as const;

            export type GeneratedApiEndpoint = typeof generatedApiContract.endpoints[number];
            export type GeneratedApiManifest = typeof generatedApiContract;
            """
        ).strip() + "\n"

    def _build_backend_controller(self, blueprint: ProjectBlueprint) -> str:
        if blueprint.slug == "sample-service":
            return self._build_sample_service_backend_controller(blueprint)

        class_name = f"Generated{blueprint.class_name}Controller"
        method_blocks = [self._build_backend_summary_method(blueprint)] + [
            self._build_backend_endpoint_method(blueprint, endpoint)
            for endpoint in self._effective_endpoints(blueprint)
        ]
        agents_list = ", ".join(f'"{self._escape_java(agent)}"' for agent in blueprint.execution_flow) or '"planner"'
        return dedent(
            f"""
            package com.axbuilder.backend.generated.{blueprint.package_slug};

            import org.springframework.http.HttpStatus;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.DeleteMapping;
            import org.springframework.web.bind.annotation.GetMapping;
            import org.springframework.web.bind.annotation.PatchMapping;
            import org.springframework.web.bind.annotation.PathVariable;
            import org.springframework.web.bind.annotation.PostMapping;
            import org.springframework.web.bind.annotation.PutMapping;
            import org.springframework.web.bind.annotation.RequestBody;
            import org.springframework.web.bind.annotation.RestController;

            import java.util.LinkedHashMap;
            import java.util.List;
            import java.util.Map;

            @RestController
            public class {class_name} {{

            {''.join(method_blocks)}
                private Map<String, Object> buildPayload(String method, String path, String description) {{
                    Map<String, Object> payload = new LinkedHashMap<>();
                    payload.put("projectId", "{blueprint.slug}");
                    payload.put("title", "{self._escape_java(blueprint.title)}");
                    payload.put("method", method);
                    payload.put("path", path);
                    payload.put("description", description);
                    payload.put("summary", "{self._escape_java(blueprint.summary)}");
                    payload.put("generatedBy", "specyn-local-runtime");
                    payload.put("executionFlow", List.of({agents_list}));
                    return payload;
                }}
            }}
            """
        ).strip() + "\n"

    def _build_sample_service_backend_controller(self, blueprint: ProjectBlueprint) -> str:
        class_name = f"Generated{blueprint.class_name}Controller"
        agents_list = ", ".join(f'"{self._escape_java(agent)}"' for agent in blueprint.execution_flow) or '"planner"'
        scenarios = ", ".join(f'"{self._escape_java(item)}"' for item in blueprint.scenarios) or '"none"'
        return dedent(
            f"""
            package com.axbuilder.backend.generated.{blueprint.package_slug};

            import org.springframework.http.HttpStatus;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.DeleteMapping;
            import org.springframework.web.bind.annotation.GetMapping;
            import org.springframework.web.bind.annotation.PathVariable;
            import org.springframework.web.bind.annotation.PatchMapping;
            import org.springframework.web.bind.annotation.PostMapping;
            import org.springframework.web.bind.annotation.RequestBody;
            import org.springframework.web.bind.annotation.RestController;

            import java.time.Instant;
            import java.util.ArrayList;
            import java.util.Collections;
            import java.util.LinkedHashMap;
            import java.util.List;
            import java.util.Map;
            import java.util.concurrent.atomic.AtomicLong;

            @RestController
            public class {class_name} {{

                private final AtomicLong sequence = new AtomicLong(0);
                private final Map<Long, Map<String, Object>> store = Collections.synchronizedMap(new LinkedHashMap<>());

                public {class_name}() {{
                    seedItem("Spec bundle 검증", "sample-service spec를 validate 하고 generated page를 확인합니다.", "DONE");
                    seedItem("런타임 확인", "새 항목을 추가하고 상태를 변경한 뒤 삭제까지 확인합니다.", "PENDING");
                }}

                @GetMapping("/api/v1/generated/{blueprint.slug}/summary")
                public Map<String, Object> generatedSummary() {{
                    Map<String, Object> payload = buildPayload("GET", "/api/v1/generated/{blueprint.slug}/summary", "generated project summary");
                    payload.put("scenarios", List.of({scenarios}));
                    payload.put("endpointCount", {len(self._effective_endpoints(blueprint))});
                    payload.put("sampleMode", "task-crud-demo");
                    payload.put("taskCount", listItems().size());
                    payload.put("sampleRoute", "/generated/{blueprint.slug}");
                    return payload;
                }}

                @GetMapping("/api/v1/tasks")
                public Map<String, Object> listTasks() {{
                    Map<String, Object> payload = buildPayload("GET", "/api/v1/tasks", "작업 목록 조회");
                    List<Map<String, Object>> tasks = listItems();
                    payload.put("items", tasks);
                    payload.put("count", tasks.size());
                    return payload;
                }}

                @GetMapping("/api/v1/tasks/{{id}}")
                public ResponseEntity<Map<String, Object>> getTask(@PathVariable Long id) {{
                    Map<String, Object> task = findStoredItem(id);
                    if (task == null) {{
                        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{{id}}"));
                    }}
                    Map<String, Object> payload = buildPayload("GET", "/api/v1/tasks/{{id}}", "작업 단건 조회");
                    payload.put("item", copyItem(task));
                    return ResponseEntity.ok(payload);
                }}

                @PostMapping("/api/v1/tasks")
                public ResponseEntity<Map<String, Object>> createTask(@RequestBody(required = false) Map<String, Object> body) {{
                    String title = readText(body, "title");
                    if (title.isBlank()) {{
                        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                                .body(errorPayload("VALIDATION_ERROR", "title 필드는 필수입니다.", "/api/v1/tasks"));
                    }}
                    String description = readText(body, "description");
                    Map<String, Object> created = seedItem(title, description, "PENDING");
                    Map<String, Object> payload = buildPayload("POST", "/api/v1/tasks", "작업 생성");
                    payload.put("item", created);
                    payload.put("count", listItems().size());
                    return ResponseEntity.status(HttpStatus.CREATED).body(payload);
                }}

                @PatchMapping("/api/v1/tasks/{{id}}/status")
                public ResponseEntity<Map<String, Object>> updateTaskStatus(@PathVariable Long id, @RequestBody(required = false) Map<String, Object> body) {{
                    Map<String, Object> task = findStoredItem(id);
                    if (task == null) {{
                        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{{id}}/status"));
                    }}

                    String status = readText(body, "status").toUpperCase();
                    if (!("PENDING".equals(status) || "DONE".equals(status))) {{
                        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                                .body(errorPayload("INVALID_STATUS", "status는 PENDING 또는 DONE 이어야 합니다.", "/api/v1/tasks/{{id}}/status"));
                    }}

                    synchronized (store) {{
                        task.put("status", status);
                        task.put("updatedAt", Instant.now().toString());
                    }}

                    Map<String, Object> payload = buildPayload("PATCH", "/api/v1/tasks/{{id}}/status", "작업 상태 변경");
                    payload.put("item", copyItem(task));
                    return ResponseEntity.ok(payload);
                }}

                @DeleteMapping("/api/v1/tasks/{{id}}")
                public ResponseEntity<?> deleteTask(@PathVariable Long id) {{
                    Map<String, Object> removed;
                    synchronized (store) {{
                        removed = store.remove(id);
                    }}
                    if (removed == null) {{
                        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{{id}}"));
                    }}
                    return ResponseEntity.noContent().build();
                }}

                private Map<String, Object> seedItem(String title, String description, String status) {{
                    long id = sequence.incrementAndGet();
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("id", id);
                    item.put("title", title);
                    item.put("description", description);
                    item.put("status", status);
                    item.put("createdAt", Instant.now().toString());
                    item.put("updatedAt", Instant.now().toString());
                    synchronized (store) {{
                        store.put(id, item);
                    }}
                    return copyItem(item);
                }}

                private List<Map<String, Object>> listItems() {{
                    List<Map<String, Object>> items;
                    synchronized (store) {{
                        items = new ArrayList<>(store.values());
                    }}
                    Collections.reverse(items);
                    List<Map<String, Object>> copied = new ArrayList<>();
                    for (Map<String, Object> item : items) {{
                        copied.add(copyItem(item));
                    }}
                    return copied;
                }}

                private Map<String, Object> findStoredItem(Long id) {{
                    synchronized (store) {{
                        return store.get(id);
                    }}
                }}

                private String readText(Map<String, Object> body, String key) {{
                    if (body == null) {{
                        return "";
                    }}
                    Object value = body.get(key);
                    return value == null ? "" : String.valueOf(value).trim();
                }}

                private Map<String, Object> errorPayload(String code, String message, String path) {{
                    Map<String, Object> payload = new LinkedHashMap<>();
                    payload.put("code", code);
                    payload.put("message", message);
                    payload.put("path", path);
                    payload.put("timestamp", Instant.now().toString());
                    return payload;
                }}

                private Map<String, Object> copyItem(Map<String, Object> item) {{
                    return new LinkedHashMap<>(item);
                }}

                private Map<String, Object> buildPayload(String method, String path, String description) {{
                    Map<String, Object> payload = new LinkedHashMap<>();
                    payload.put("projectId", "{blueprint.slug}");
                    payload.put("title", "{self._escape_java(blueprint.title)}");
                    payload.put("method", method);
                    payload.put("path", path);
                    payload.put("description", description);
                    payload.put("summary", "{self._escape_java(blueprint.summary)}");
                    payload.put("generatedBy", "specyn-local-runtime");
                    payload.put("executionFlow", List.of({agents_list}));
                    return payload;
                }}
            }}
            """
        ).strip() + "\n"

    def _build_backend_summary_method(self, blueprint: ProjectBlueprint) -> str:
        scenarios = ", ".join(f'"{self._escape_java(item)}"' for item in blueprint.scenarios) or '"none"'
        return dedent(
            f"""
                @GetMapping("/api/v1/generated/{blueprint.slug}/summary")
                public Map<String, Object> generatedSummary() {{
                    Map<String, Object> payload = buildPayload("GET", "/api/v1/generated/{blueprint.slug}/summary", "generated project summary");
                    payload.put("scenarios", List.of({scenarios}));
                    payload.put("endpointCount", {len(self._effective_endpoints(blueprint))});
                    return payload;
                }}

            """
        )

    def _build_backend_endpoint_method(self, blueprint: ProjectBlueprint, endpoint: ApiEndpoint) -> str:
        annotation = {
            "GET": "GetMapping",
            "POST": "PostMapping",
            "PUT": "PutMapping",
            "PATCH": "PatchMapping",
            "DELETE": "DeleteMapping",
        }.get(endpoint.method, "GetMapping")
        params: list[str] = []
        body_line = ""
        for variable in endpoint.path_variables:
            params.append(f'@PathVariable String {variable}')
        if endpoint.request_body_allowed:
            params.append('@RequestBody(required = false) Map<String, Object> body')
            body_line = '        if (body != null) {\n            payload.put("requestBody", body);\n        }\n'
        param_signature = ", ".join(params)
        path_variables_block = "\n".join(f'        payload.put("{variable}", {variable});' for variable in endpoint.path_variables)
        if path_variables_block:
            path_variables_block += "\n"
        if endpoint.response_status == 204:
            return dedent(
                f"""
                    @{annotation}("{endpoint.path}")
                    public ResponseEntity<Void> {endpoint.java_method_name}({param_signature}) {{
                        return ResponseEntity.noContent().build();
                    }}

                """
            )
        return dedent(
            f"""
                @{annotation}("{endpoint.path}")
                public ResponseEntity<Map<String, Object>> {endpoint.java_method_name}({param_signature}) {{
                    Map<String, Object> payload = buildPayload("{endpoint.method}", "{endpoint.path}", "{self._escape_java(endpoint.description)}");
            {path_variables_block}{body_line}        return ResponseEntity.status(HttpStatus.valueOf({endpoint.response_status})).body(payload);
                }}

            """
        )

    def _build_ai_server_router(self, blueprint: ProjectBlueprint) -> str:
        manifest_json = json.dumps(blueprint_to_manifest(blueprint), ensure_ascii=False, indent=2)
        return (
            "import json\n\n"
            "from fastapi import APIRouter\n\n"
            f"router = APIRouter(prefix=\"/generated/{blueprint.slug}\", tags=[\"generated\", \"{blueprint.slug}\"])\n\n"
            f"GENERATED_MANIFEST = json.loads('''{manifest_json}''')\n\n"
            "@router.get(\"/context\")\n"
            "async def generated_context() -> dict:\n"
            "    return GENERATED_MANIFEST\n"
        )

    def _build_frontend_page(self, blueprint: ProjectBlueprint) -> str:
        if blueprint.slug == "sample-service":
            return self._build_sample_service_frontend_page(blueprint)

        endpoint_rows = ",\n  ".join(
            json.dumps({
                "method": endpoint.method,
                "path": endpoint.path,
                "description": endpoint.description,
                "auth": endpoint.auth,
                "note": endpoint.note,
            }, ensure_ascii=False)
            for endpoint in self._effective_endpoints(blueprint)
        )
        return dedent(
            f"""
            import {{ useEffect, useState }} from "react";

            import {{ generatedApiContract }} from "./apiContract";

            const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8080";
            const ENDPOINTS = [
              {endpoint_rows}
            ] as const;

            export default function GeneratedProjectPage() {{
              const [summaryPayload, setSummaryPayload] = useState<string>("loading...");

              useEffect(() => {{
                let cancelled = false;
                async function loadSummary() {{
                  try {{
                    const response = await fetch(BACKEND_URL + "/api/v1/generated/{blueprint.slug}/summary");
                    const payload = await response.json();
                    if (!cancelled) {{
                      setSummaryPayload(JSON.stringify(payload, null, 2));
                    }}
                  }} catch (error) {{
                    if (!cancelled) {{
                      const message = error instanceof Error ? error.message : String(error);
                      setSummaryPayload("failed to load summary: " + message);
                    }}
                  }}
                }}
                void loadSummary();
                return () => {{
                  cancelled = true;
                }};
              }}, []);

              return (
                <section className="page-grid">
                  <article className="panel">
                    <h2>{blueprint.title} · Generated Project Page</h2>
                    <p>{blueprint.summary}</p>
                    <p>
                      이 페이지는 <code>specyn run --spec-dir ...</code> 실행 시 생성된 산출물입니다.
                      생성된 API contract와 backend summary endpoint를 바로 확인할 수 있습니다.
                    </p>
                  </article>

                  <article className="panel">
                    <h2>요약</h2>
                    <pre>{{summaryPayload}}</pre>
                  </article>

                  <article className="panel">
                    <h2>Endpoint Contract</h2>
                    <pre>{{JSON.stringify(generatedApiContract, null, 2)}}</pre>
                  </article>

                  <article className="panel">
                    <h2>Endpoints</h2>
                    <div className="results-grid">
                      {{ENDPOINTS.map((endpoint) => (
                        <article className="result-card" key={{endpoint.method + "-" + endpoint.path}}>
                          <h3>{{endpoint.method}} {{endpoint.path}}</h3>
                          <p>{{endpoint.description}}</p>
                          <p><strong>인증:</strong> {{endpoint.auth}}</p>
                          <p><strong>비고:</strong> {{endpoint.note || "-"}}</p>
                        </article>
                      ))}}
                    </div>
                  </article>
                </section>
              );
            }}
            """
        ).strip() + "\n"

    def _build_sample_service_frontend_page(self, blueprint: ProjectBlueprint) -> str:
        endpoint_rows = ",\n  ".join(
            json.dumps(
                {
                    "method": endpoint.method,
                    "path": endpoint.path,
                    "description": endpoint.description,
                    "auth": endpoint.auth,
                    "note": endpoint.note,
                },
                ensure_ascii=False,
            )
            for endpoint in self._effective_endpoints(blueprint)
        )
        return dedent(
            f"""
            import {{ FormEvent, useEffect, useState }} from "react";

            import {{ generatedApiContract }} from "./apiContract";

            const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8080";
            const SUMMARY_URL = BACKEND_URL + "/api/v1/generated/{blueprint.slug}/summary";
            const TASKS_URL = BACKEND_URL + "/api/v1/tasks";

            type TaskItem = {{
              id: number;
              title: string;
              description?: string;
              status: string;
              createdAt?: string;
              updatedAt?: string;
            }};

            type TasksPayload = {{ items?: TaskItem[] }};
            type TaskPayload = {{ item?: TaskItem }};

            const ENDPOINTS = [
              {endpoint_rows}
            ] as const;

            async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {{
              const response = await fetch(url, {{
                ...init,
                headers: {{
                  "Content-Type": "application/json",
                  ...(init?.headers ?? {{}}),
                }},
              }});

              const text = await response.text();
              const payload = text ? JSON.parse(text) : null;
              if (!response.ok) {{
                const message =
                  payload && typeof payload === "object" && "message" in payload && typeof (payload as {{ message?: unknown }}).message === "string"
                    ? String((payload as {{ message: string }}).message)
                    : `${{response.status}} ${{response.statusText}}`;
                throw new Error(message);
              }}
              return payload as T;
            }}

            async function requestNoContent(url: string, init?: RequestInit): Promise<void> {{
              const response = await fetch(url, init);
              if (!response.ok) {{
                const text = await response.text();
                const payload = text ? JSON.parse(text) : null;
                const message =
                  payload && typeof payload === "object" && "message" in payload && typeof (payload as {{ message?: unknown }}).message === "string"
                    ? String((payload as {{ message: string }}).message)
                    : `${{response.status}} ${{response.statusText}}`;
                throw new Error(message);
              }}
            }}

            function taskDetailUrl(id: number): string {{
              return BACKEND_URL + `/api/v1/tasks/${{id}}`;
            }}

            function taskStatusUrl(id: number): string {{
              return BACKEND_URL + `/api/v1/tasks/${{id}}/status`;
            }}

            export default function GeneratedProjectPage() {{
              const [tasks, setTasks] = useState<TaskItem[]>([]);
              const [summaryPayload, setSummaryPayload] = useState<string>("loading...");
              const [detailPayload, setDetailPayload] = useState<string>("목록에서 '상세 보기'를 누르면 개별 GET 응답을 확인할 수 있습니다.");
              const [title, setTitle] = useState("");
              const [description, setDescription] = useState("");
              const [loading, setLoading] = useState(true);
              const [submitting, setSubmitting] = useState(false);
              const [errorMessage, setErrorMessage] = useState<string | null>(null);
              const [selectedId, setSelectedId] = useState<number | null>(null);

              async function refreshSummary(): Promise<void> {{
                const payload = await fetchJson<Record<string, unknown>>(SUMMARY_URL);
                setSummaryPayload(JSON.stringify(payload, null, 2));
              }}

              async function refreshTasks(): Promise<TaskItem[]> {{
                const payload = await fetchJson<TasksPayload>(TASKS_URL);
                const items = Array.isArray(payload.items) ? payload.items : [];
                setTasks(items);
                return items;
              }}

              async function refreshAll(): Promise<void> {{
                setLoading(true);
                setErrorMessage(null);
                try {{
                  await Promise.all([refreshSummary(), refreshTasks()]);
                }} catch (error) {{
                  const message = error instanceof Error ? error.message : String(error);
                  setErrorMessage(message);
                }} finally {{
                  setLoading(false);
                }}
              }}

              useEffect(() => {{
                void refreshAll();
              }}, []);

              async function loadTaskDetail(id: number): Promise<void> {{
                const payload = await fetchJson<TaskPayload>(taskDetailUrl(id));
                setSelectedId(id);
                setDetailPayload(JSON.stringify(payload, null, 2));
              }}

              async function handleCreate(event: FormEvent<HTMLFormElement>): Promise<void> {{
                event.preventDefault();
                setSubmitting(true);
                setErrorMessage(null);
                try {{
                  const payload = await fetchJson<TaskPayload>(TASKS_URL, {{
                    method: "POST",
                    body: JSON.stringify({{ title, description }}),
                  }});
                  setTitle("");
                  setDescription("");
                  await refreshSummary();
                  await refreshTasks();
                  if (payload.item?.id) {{
                    await loadTaskDetail(payload.item.id);
                  }}
                }} catch (error) {{
                  const message = error instanceof Error ? error.message : String(error);
                  setErrorMessage(message);
                }} finally {{
                  setSubmitting(false);
                }}
              }}

              async function handleToggleStatus(task: TaskItem): Promise<void> {{
                const nextStatus = task.status === "DONE" ? "PENDING" : "DONE";
                setErrorMessage(null);
                try {{
                  await fetchJson<TaskPayload>(taskStatusUrl(task.id), {{
                    method: "PATCH",
                    body: JSON.stringify({{ status: nextStatus }}),
                  }});
                  await refreshSummary();
                  await refreshTasks();
                  await loadTaskDetail(task.id);
                }} catch (error) {{
                  const message = error instanceof Error ? error.message : String(error);
                  setErrorMessage(message);
                }}
              }}

              async function handleDelete(taskId: number): Promise<void> {{
                setErrorMessage(null);
                try {{
                  await requestNoContent(taskDetailUrl(taskId), {{ method: "DELETE" }});
                  const items = await refreshTasks();
                  await refreshSummary();
                  if (selectedId === taskId) {{
                    setSelectedId(null);
                    setDetailPayload("삭제된 항목입니다. 다른 항목을 선택하거나 새 작업을 생성해 보세요.");
                  }}
                  if (items.length === 0) {{
                    setDetailPayload("현재 등록된 작업이 없습니다. 위 폼에서 새 작업을 생성해 보세요.");
                  }}
                }} catch (error) {{
                  const message = error instanceof Error ? error.message : String(error);
                  setErrorMessage(message);
                }}
              }}

              return (
                <section className="page-grid">
                  <article className="panel">
                    <h2>{blueprint.title} · Generated CRUD Demo</h2>
                    <p>{blueprint.summary}</p>
                    <p>
                      이 페이지는 <code>specyn run</code> 실행으로 생성된 간단한 작업 관리 웹사이트입니다.
                      아래에서 생성, 상세 조회, 상태 변경, 삭제를 모두 확인할 수 있습니다.
                    </p>
                    <ul className="stack-list">
                      {{generatedApiContract.scenarios.map((scenario) => (
                        <li key={{scenario}}>{{scenario}}</li>
                      ))}}
                    </ul>
                  </article>

                  <article className="panel">
                    <div className="panel-header">
                      <h2>새 작업 생성</h2>
                      <button type="button" className="secondary-button" onClick={{() => void refreshAll()}} disabled={{loading}}>
                        새로고침
                      </button>
                    </div>
                    <form className="form-grid" onSubmit={{(event) => void handleCreate(event)}}>
                      <label>
                        제목
                        <input value={{title}} onChange={{(event) => setTitle(event.target.value)}} placeholder="예: README 업데이트" />
                      </label>
                      <label>
                        설명
                        <textarea value={{description}} onChange={{(event) => setDescription(event.target.value)}} placeholder="예: generated page와 backend API를 함께 확인한다." />
                      </label>
                      <div className="button-row">
                        <button type="submit" disabled={{submitting}}>
                          {{submitting ? "저장 중..." : "작업 생성"}}
                        </button>
                      </div>
                    </form>
                    {{errorMessage ? <div className="error-box">{{errorMessage}}</div> : null}}
                  </article>

                  <article className="panel">
                    <h2>현재 작업 목록</h2>
                    {{loading ? <p>작업을 불러오는 중입니다...</p> : null}}
                    {{!loading && tasks.length === 0 ? <p>아직 등록된 작업이 없습니다.</p> : null}}
                    <div className="results-grid">
                      {{tasks.map((task) => (
                        <article className="result-card" key={{task.id}}>
                          <div className="panel-header">
                            <h3>{{task.title}}</h3>
                            <span className={{`status-badge ${{task.status === "DONE" ? "status-done" : "status-pending"}}`}}>
                              {{task.status}}
                            </span>
                          </div>
                          <p className="muted-text">ID: {{task.id}}</p>
                          <p>{{task.description || "설명이 없습니다."}}</p>
                          <div className="button-row">
                            <button type="button" className="secondary-button" onClick={{() => void loadTaskDetail(task.id)}}>
                              상세 보기
                            </button>
                            <button type="button" onClick={{() => void handleToggleStatus(task)}}>
                              상태 토글
                            </button>
                            <button type="button" className="secondary-button" onClick={{() => void handleDelete(task.id)}}>
                              삭제
                            </button>
                          </div>
                        </article>
                      ))}}
                    </div>
                  </article>

                  <article className="panel">
                    <h2>선택한 작업 상세</h2>
                    <p className="muted-text">
                      {{selectedId === null ? "선택된 작업이 없습니다." : `선택된 ID: ${{selectedId}}`}}
                    </p>
                    <pre>{{detailPayload}}</pre>
                  </article>

                  <article className="panel">
                    <h2>Generated Summary</h2>
                    <pre>{{summaryPayload}}</pre>
                  </article>

                  <article className="panel">
                    <h2>API Contract</h2>
                    <pre>{{JSON.stringify(generatedApiContract, null, 2)}}</pre>
                  </article>

                  <article className="panel">
                    <h2>Endpoints</h2>
                    <div className="results-grid">
                      {{ENDPOINTS.map((endpoint) => (
                        <article className="result-card" key={{endpoint.method + "-" + endpoint.path}}>
                          <h3>{{endpoint.method}} {{endpoint.path}}</h3>
                          <p>{{endpoint.description}}</p>
                          <p><strong>인증:</strong> {{endpoint.auth}}</p>
                          <p><strong>비고:</strong> {{endpoint.note || "-"}}</p>
                        </article>
                      ))}}
                    </div>
                  </article>
                </section>
              );
            }}
            """
        ).strip() + "\n"

    def _build_sql_blueprint(self, blueprint: ProjectBlueprint) -> str:
        if blueprint.slug == "sample-service":
            return dedent(
                f"""
                -- Generated by Specyn local runtime for {blueprint.slug}
                create table if not exists {blueprint.package_slug}_tasks (
                    id bigint generated always as identity primary key,
                    title varchar(200) not null,
                    description varchar(1000),
                    status varchar(32) not null default 'PENDING',
                    created_at timestamp not null default current_timestamp,
                    updated_at timestamp not null default current_timestamp
                );

                create index if not exists idx_{blueprint.package_slug}_tasks_status
                    on {blueprint.package_slug}_tasks (status);
                """
            ).strip() + "\n"

        table_name = blueprint.package_slug
        return dedent(
            f"""
            -- Generated by Specyn local runtime for {blueprint.slug}
            create table if not exists {table_name}_records (
                id bigint generated always as identity primary key,
                external_id varchar(128) not null,
                payload json not null,
                created_at timestamp not null default current_timestamp,
                updated_at timestamp not null default current_timestamp,
                constraint uk_{table_name}_external_id unique (external_id)
            );

            create index if not exists idx_{table_name}_created_at on {table_name}_records (created_at desc);
            """
        ).strip() + "\n"

    def _build_generated_compose(self, blueprint: ProjectBlueprint) -> str:
        return dedent(
            f"""
            services:
              {blueprint.slug}-backend:
                image: eclipse-temurin:21-jre
                working_dir: /workspace/backend
                command: ["./gradlew", "bootRun"]
              {blueprint.slug}-ai-server:
                image: python:3.13-slim
                working_dir: /workspace
                command: ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "ai-server", "--host", "0.0.0.0", "--port", "8000"]
              {blueprint.slug}-frontend:
                image: node:24-alpine
                working_dir: /workspace/frontend
                command: ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
            """
        ).strip() + "\n"

    def _build_ai_server_test(self, blueprint: ProjectBlueprint) -> str:
        return dedent(
            f"""
            import pathlib
            import sys

            from fastapi.testclient import TestClient

            ROOT = pathlib.Path(__file__).resolve().parents[3]
            sys.path.insert(0, str(ROOT / "ai-server"))

            from app.main import app  # noqa: E402


            client = TestClient(app)


            def test_generated_{blueprint.package_slug}_context_route() -> None:
                response = client.get("/generated/{blueprint.slug}/context")
                assert response.status_code == 200
                payload = response.json()
                assert payload["projectId"] == "{blueprint.slug}"
                assert payload["executionFlow"]
            """
        ).strip() + "\n"

    def _build_test_plan(self, blueprint: ProjectBlueprint) -> str:
        scenarios = [f"- {scenario}" for scenario in blueprint.test_scenarios] or ["- 시나리오를 spec에 추가해 주세요."]
        if blueprint.slug == "sample-service":
            automation_checks = [
                "- generated backend summary endpoint가 응답한다.",
                "- GET /api/v1/tasks 로 seeded task와 새로 생성한 task를 모두 확인할 수 있다.",
                "- POST /api/v1/tasks 로 title/description을 가진 task를 생성할 수 있다.",
                "- PATCH /api/v1/tasks/{id}/status 로 DONE/PENDING 전환을 검증한다.",
                "- DELETE /api/v1/tasks/{id} 이후 재조회 시 404를 확인한다.",
                "- generated frontend page에서 생성/상태 변경/삭제를 수동 QA로 재현한다.",
            ]
        else:
            automation_checks = [
                "- generated backend summary endpoint가 응답한다.",
                "- generated ai-server context route가 응답한다.",
                "- generated frontend page가 endpoint contract를 표시한다.",
            ]

        lines = [
            f"# {blueprint.title} Generated Test Plan",
            "",
            "## 목적",
            blueprint.summary,
            "",
            "## 우선 검증 시나리오",
            *scenarios,
            "",
            "## 자동화 확인 포인트",
            *automation_checks,
        ]
        return "\n".join(lines).strip() + "\n"

    def _build_project_doc(self, blueprint: ProjectBlueprint) -> str:
        endpoints = [f"- `{endpoint.method} {endpoint.path}` · {endpoint.description}" for endpoint in self._effective_endpoints(blueprint)] or ["- generated endpoint 없음"]
        execution_flow = [f"- {agent}" for agent in blueprint.execution_flow]
        if blueprint.slug == "sample-service":
            lines = [
                f"# {blueprint.title}",
                "",
                "이 문서는 `specyn run` 로컬 실행 결과로 생성된 sample-service CRUD 데모 요약입니다.",
                "",
                "## 프로젝트 요약",
                blueprint.summary,
                "",
                "## 실행된 Agent",
                *execution_flow,
                "",
                "## 생성된 확인 포인트",
                f"- Frontend: `/generated/{blueprint.slug}` 라우트",
                f"- Backend summary: `/api/v1/generated/{blueprint.slug}/summary`",
                "- Backend CRUD: `/api/v1/tasks`, `/api/v1/tasks/{id}`, `/api/v1/tasks/{id}/status`",
                f"- AI Server: `/generated/{blueprint.slug}/context`",
                "",
                "## Endpoint 초안",
                *endpoints,
                "",
                "## 실제 확인 순서",
                "1. `python scripts/specyn_tasks.py dev` 로 전체 스택을 실행합니다.",
                f"2. `http://localhost:5173/generated/{blueprint.slug}` 에 접속합니다.",
                "3. 새 작업을 생성하고 상세 보기를 눌러 개별 GET 응답을 확인합니다.",
                "4. 상태 토글과 삭제를 수행해 프런트엔드와 백엔드가 함께 반응하는지 확인합니다.",
            ]
            return "\n".join(lines).strip() + "\n"

        lines = [
            f"# {blueprint.title}",
            "",
            "이 문서는 `specyn run` 로컬 실행 결과로 생성된 프로젝트 요약입니다.",
            "",
            "## 프로젝트 요약",
            blueprint.summary,
            "",
            "## 실행된 Agent",
            *execution_flow,
            "",
            "## 생성된 확인 포인트",
            f"- Frontend: `/generated/{blueprint.slug}` 라우트",
            f"- Backend: `/api/v1/generated/{blueprint.slug}/summary`",
            f"- AI Server: `/generated/{blueprint.slug}/context`",
            "",
            "## Endpoint 초안",
            *endpoints,
        ]
        return "\n".join(lines).strip() + "\n"

    def _escape_java(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')
