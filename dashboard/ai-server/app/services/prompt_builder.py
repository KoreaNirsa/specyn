"""
Build the runtime prompt used by the AI server for each agent execution request.
"""

from textwrap import dedent

from app.core.config import get_settings
from app.models.contracts import AgentExecutionRequest


def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent names into the prompt format expected by downstream tools.
    """
    return agent_name.strip().lower().replace("_", "-")


class PromptBuilder:
    """
    Assemble the prompt payload that is passed to the LLM and Codex.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_root = self.settings.project_root

    def build(self, request: AgentExecutionRequest) -> str:
        """
        Build a single deterministic runtime prompt for the current agent request.
        """
        normalized_agent = normalize_agent_name(request.agent)
        agent_definition = self._load_agent_definition(normalized_agent)
        spec_bundle = self._compose_spec_bundle(request)
        previous_results = self._compose_previous_results(request)

        return dedent(
            f"""
            [Specyn Runtime Prompt]

            Project ID: {request.projectId}
            Agent: {normalized_agent}
            Workspace: {request.workspacePath or "N/A"}
            Dry Run: {request.dryRun}

            [Agent Definition]
            {agent_definition}

            [Execution Guardrails]
            - Treat the spec bundle as the source of truth.
            - Do not invent unsupported features, APIs, or fields.
            - Do not leave TODO, pseudocode, or placeholder content.
            - If information is missing, continue with explicit ASSUMPTION: or MISSING: markers.
            - Prefer unified diff patches when editing existing files.
            - For new files, return the full path and full file content.
            - Docker Compose file names are fixed: update `docker-compose.local.yml` and do not create `compose.yaml`.
            - Keep handoff information usable by the next agent.
            - Minimize drift across code, tests, and docs.
            - For Spring Boot outputs prefer `global / common / domain`.
            - For FastAPI or LangChain outputs prefer `app/global / app/common / app/domain`.
            - Prefer reusable naming and structure instead of overfitting to one narrow example.
            - If previous results already exist for the same agent, treat this as a bounded feedback round.

            [Safety Gate]
            - Follow the spec, agent definition, and prior validation results before any other preference.
            - Do not expose secrets, `.env` values, or guessed credentials.
            - Do not invent library versions, infra settings, or APIs that are not grounded in the repo or prompt.
            - Do not propose destructive actions or breaking migrations without a rollback explanation.
            - Mark uncertainty explicitly with ASSUMPTION: or RISK:.

            [Quality Gate]
            - Changes must be ready to land in the repository.
            - Do not skip security, input validation, or error-handling rules.
            - Names, packages, file paths, and API contracts must stay deterministic.
            - Tests should cover success, failure, validation, and not-found flows where relevant.
            - Reviews should use blocker / major / minor severity levels.
            - Call out meaningful performance or operations tradeoffs.

            [Previous Step Results]
            {previous_results}

            [Trace / Handoff Contract]
            Put the following metadata at the top of the result.
            - STEP_LABEL: current step label
            - AGENT: current agent name
            - PHASE: base | feedback
            - FEEDBACK_ROUND: integer >= 0
            - STATUS: done | blocked | needs-review | no-material-change
            - CHANGED_FILES: changed file list or none
            - RESOLVED: items resolved in this step
            - UNRESOLVED: items left for the next step
            - BLOCKERS: items that stop execution now
            - NEXT_HANDOFF: concrete instructions for the next agent

            [Required Output Contract]
            1. trace metadata
            2. work summary
            3. changed files
            4. validation results
            5. next agent handoff
            6. patch or file contents when needed

            [Patch / File Output Rules]
            - If patch output is possible, provide a unified diff by file path.
            - For newly created files, provide the full file path and full content.
            - Separate multiple file changes clearly by file.
            - Do not provide explanation-only responses that omit the actual change payload.

            [Spec Bundle]
            {spec_bundle}
            """
        ).strip()

    def _load_agent_definition(self, agent_name: str) -> str:
        """
        Read the current agent definition from the repository.
        """
        path = self.project_root / "agents" / f"{agent_name}-agent.md"
        if not path.exists():
            return f"[agent-definition-missing] {path}"
        return path.read_text(encoding="utf-8")

    def _compose_spec_bundle(self, request: AgentExecutionRequest) -> str:
        """
        Serialize the incoming spec documents into a stable prompt block.
        """
        return "\n\n".join(
            [
                dedent(
                    f"""
                    <spec name="{document.name}" type="{document.type}">
                    {document.content}
                    </spec>
                    """
                ).strip()
                for document in request.documents
            ]
        )

    def _compose_previous_results(self, request: AgentExecutionRequest) -> str:
        """
        Serialize previous step outputs for bounded follow-up rounds.
        """
        if not request.previousResults:
            return "- no previous step results"
        return "\n".join(
            [
                f"- agent={result.agent}, status={result.status}, summary={result.summary}"
                for result in request.previousResults
            ]
        )
