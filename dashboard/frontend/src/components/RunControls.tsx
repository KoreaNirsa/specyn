import { useMemo, useState } from "react";

import { useRunSpecBundle } from "../hooks/useRunSpecBundle";
import { useI18n } from "../i18n";
import { useWorkspaceStore } from "../store/workspaceStore";
import { StatusBadge } from "./StatusBadge";

const PROJECT_ID = "sample-service";
const WORKSPACE_PATH = "projects/sample-service";

/**
 * Run controls for the current workflow.
 */
export function RunControls() {
  const { t } = useI18n();
  const mutation = useRunSpecBundle();
  const runStatus = useWorkspaceStore((state) => state.runStatus);
  const currentWorkspacePath = useWorkspaceStore((state) => state.currentWorkspacePath);
  const eventTrace = useWorkspaceStore((state) => state.eventTrace);
  const results = useWorkspaceStore((state) => state.results);
  const [ragEnabled, setRagEnabled] = useState(false);

  const progress = useMemo(() => {
    let totalSteps = 0;
    let completedSteps = 0;
    let activeAgent: string | null = null;
    let activeStepIndex: number | null = null;
    const agentStates = new Map<string, { agent: string; status: string; progress: number }>();

    for (const event of eventTrace) {
      if (event.totalSteps && event.totalSteps > totalSteps) {
        totalSteps = event.totalSteps;
      }

      if ((event.type === "step-start" || event.type === "step-log") && event.agent) {
        activeAgent = event.agent;
        activeStepIndex = event.stepIndex ?? activeStepIndex;
        agentStates.set(event.agent, {
          agent: event.agent,
          status: "RUNNING",
          progress: 50,
        });
      }

      if (event.type === "step-complete" && event.agent) {
        completedSteps += 1;
        agentStates.set(event.agent, {
          agent: event.agent,
          status: event.status ?? "COMPLETED",
          progress: 100,
        });
        if (activeAgent === event.agent) {
          activeAgent = null;
          activeStepIndex = null;
        }
      }

      if (event.type === "run-complete" || event.type === "run-error") {
        activeAgent = null;
        activeStepIndex = null;
      }
    }

    if (!totalSteps) {
      totalSteps = Math.max(results.length, agentStates.size, mutation.isPending ? 1 : 0);
    }

    const percent = totalSteps
      ? Math.min(
          100,
          Math.round(((completedSteps + (activeAgent ? 0.5 : 0)) / totalSteps) * 100),
        )
      : 0;

    return {
      totalSteps,
      completedSteps,
      activeAgent,
      activeStepIndex,
      percent,
      agentStates: Array.from(agentStates.values()),
    };
  }, [eventTrace, mutation.isPending, results.length]);

  /**
   * Handle on submit for the current workflow.
   */
  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutation.mutateAsync({
      projectId: PROJECT_ID,
      workspacePath: WORKSPACE_PATH,
      ragEnabled,
    });
  }

  return (
    <section className="panel control-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">{t("run.eyebrow")}</p>
          <h3>{t("run.title")}</h3>
        </div>
        <StatusBadge
          label={
            mutation.isPending
              ? t("common.status.running")
              : mutation.isError
                ? t("common.status.error")
                : runStatus
          }
          tone={
            mutation.isPending
              ? "warning"
              : mutation.isError
                ? "danger"
                : runStatus === "FAILED"
                  ? "danger"
                  : "success"
          }
        />
      </div>
      <p className="panel-copy">
        {t("run.description")} <code>{WORKSPACE_PATH}</code>.
        {currentWorkspacePath ? t("run.currentWorkspace", { workspace: currentWorkspacePath }) : ""}
      </p>
      <form className="control-form" onSubmit={onSubmit}>
        <label>
          <span>{t("run.projectId")}</span>
          <input value={PROJECT_ID} disabled readOnly />
        </label>
        <label>
          <span>{t("run.workspacePath")}</span>
          <input value={WORKSPACE_PATH} disabled readOnly />
        </label>
        <label className="checkbox-row">
          <input
            checked={ragEnabled}
            onChange={(event) => setRagEnabled(event.target.checked)}
            type="checkbox"
          />
          <span>{t("run.enableRag")}</span>
        </label>
        <div className="action-row">
          <button className="primary-button" disabled={mutation.isPending} type="submit">
            {mutation.isPending ? t("run.running") : t("run.primary")}
          </button>
          <button className="secondary-button" disabled type="button">
            {t("run.validatePlanned")}
          </button>
          <button className="secondary-button" disabled type="button">
            {t("run.compilePlanned")}
          </button>
        </div>
      </form>
      <div className="run-progress-card">
        <div className="run-progress-card__header">
          <div>
            <p className="panel-eyebrow">Run Progress</p>
            <h4>{progress.percent}%</h4>
          </div>
          <StatusBadge
            label={progress.activeAgent ? "IN PROGRESS" : runStatus}
            tone={progress.activeAgent ? "warning" : runStatus === "FAILED" ? "danger" : "success"}
          />
        </div>
        <div aria-hidden="true" className="progress-bar">
          <span style={{ width: `${progress.percent}%` }} />
        </div>
        <p className="panel-copy">
          {progress.activeAgent
            ? `Current agent: ${progress.activeAgent} (${progress.activeStepIndex ?? "?"}/${progress.totalSteps || "?"})`
            : progress.totalSteps
              ? `Completed steps: ${progress.completedSteps}/${progress.totalSteps}`
              : "Waiting to start"}
        </p>
        {progress.agentStates.length > 0 ? (
          <div className="progress-chip-row">
            {progress.agentStates.map((agentState) => (
              <article className="progress-chip" key={agentState.agent}>
                <strong>{agentState.agent}</strong>
                <span>{agentState.progress}%</span>
              </article>
            ))}
          </div>
        ) : null}
      </div>
      {mutation.isError ? (
        <p className="error-text">
          {mutation.error instanceof Error
            ? `${t("run.errorPrefix")}: ${mutation.error.message}`
            : t("timeline.runFailed")}
        </p>
      ) : null}
      <div className="placeholder-grid">
        <article className="placeholder-card">
          <div className="placeholder-card__header">
            <h4>{t("run.futureQuality")}</h4>
            <StatusBadge label={t("common.status.planned")} tone="warning" />
          </div>
          <ul>
            <li>{t("run.schemaAlignment")}</li>
            <li>{t("run.promptDrift")}</li>
            <li>{t("run.memorySnapshot")}</li>
            <li>{t("run.policyGate")}</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
