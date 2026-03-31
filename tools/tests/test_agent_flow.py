from pathlib import Path

from tools.agent_flow import build_execution_plan, resolve_agent_flow
from tools.spec_loader import load_spec_bundle


def test_resolve_agent_flow_uses_agent_spec_execution_flow() -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    flow = resolve_agent_flow(bundle, rag_enabled=False)

    assert flow.execution_flow == [
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
    ]
    assert flow.max_feedback_rounds == 2
    assert [loop.name for loop in flow.feedback_loops] == [
        "api-backend-contract-sync",
        "design-frontend-ux-sync",
        "backend-dba-persistence-hardening",
        "review-docs-release-sync",
    ]


def test_resolve_agent_flow_inserts_rag_after_planner_when_enabled() -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    flow = resolve_agent_flow(bundle, rag_enabled=True)

    assert flow.execution_flow[0:3] == ["planner", "rag", "design"]


def test_build_execution_plan_expands_bounded_feedback_loops() -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    execution_plan = build_execution_plan(bundle, rag_enabled=False)
    labels = [step.label for step in execution_plan]
    agents = [step.agent for step in execution_plan]

    assert agents == [
        "planner",
        "design",
        "api",
        "backend",
        "api",
        "backend",
        "api",
        "backend",
        "frontend",
        "design",
        "frontend",
        "design",
        "frontend",
        "dba",
        "backend",
        "dba",
        "backend",
        "dba",
        "devops",
        "test",
        "code-analysis",
        "security",
        "performance",
        "review",
        "docs",
        "review",
        "docs",
        "review",
        "docs",
        "final-review",
    ]
    assert labels[4].endswith("api-api-backend-contract-sync-r1")
    assert labels[6].endswith("api-api-backend-contract-sync-r2")
    assert labels[25].endswith("review-review-docs-release-sync-r1")
    assert labels[27].endswith("review-review-docs-release-sync-r2")
