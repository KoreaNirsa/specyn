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
