"""
spec bundle 검증과 agent 흐름 계산에 필요한 상수 계약을 한곳에 모아 둔 모듈이다.
필수 spec 타입, 필수 섹션, 지원 agent 목록, 기본 실행 흐름, 파일 생성 agent 집합을 공유 정의로 유지해 validator와 runtime의 해석 기준을 일치시킨다.
"""

from __future__ import annotations

REQUIRED_SPEC_TYPES = {"product", "api", "test", "review", "agent"}
REQUIRED_SECTIONS = {"목적", "입력", "출력", "실행 규칙", "Validation 기준", "Prompt"}
REQUIRED_PROMPT_SUBSECTIONS = {"Role", "Instructions", "Format"}
KNOWN_AGENT_NAMES = {
    "planner",
    "design",
    "api",
    "backend",
    "frontend",
    "dba",
    "devops",
    "test",
    "code-analysis",
    "security",
    "performance",
    "review",
    "docs",
    "final-review",
    "rag",
    "orchestrator",
}
DEFAULT_AGENT_FLOW = ["planner", "api", "test", "review", "docs", "final-review"]
REQUIRED_FLOW_AGENTS = {"planner", "api", "test", "review", "docs", "final-review"}
FILE_GENERATING_AGENTS = {"api", "backend", "frontend", "dba", "devops", "test", "docs"}
