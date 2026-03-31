import { useState } from "react";

import { useRunSpecBundle } from "../hooks/useRunSpecBundle";
import { StatusBadge } from "./StatusBadge";

export function RunControls() {
  const mutation = useRunSpecBundle();
  const [projectId, setProjectId] = useState("sample-service");
  const [workspacePath, setWorkspacePath] = useState(".workspace/sample-service");
  const [ragEnabled, setRagEnabled] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await mutation.mutateAsync({ projectId, workspacePath, ragEnabled });
  }

  return (
    <section className="panel control-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Run Studio</p>
          <h3>Current Runtime Controls</h3>
        </div>
        <StatusBadge
          label={mutation.isPending ? "RUNNING" : mutation.isError ? "ERROR" : "READY"}
          tone={mutation.isPending ? "warning" : mutation.isError ? "danger" : "success"}
        />
      </div>
      <form className="control-form" onSubmit={onSubmit}>
        <label>
          <span>Project ID</span>
          <input value={projectId} onChange={(event) => setProjectId(event.target.value)} />
        </label>
        <label>
          <span>Workspace Path</span>
          <input
            value={workspacePath}
            onChange={(event) => setWorkspacePath(event.target.value)}
          />
        </label>
        <label className="checkbox-row">
          <input
            checked={ragEnabled}
            onChange={(event) => setRagEnabled(event.target.checked)}
            type="checkbox"
          />
          <span>Enable RAG during backend execution</span>
        </label>
        <div className="action-row">
          <button className="primary-button" disabled={mutation.isPending} type="submit">
            {mutation.isPending ? "Running..." : "Run Current Spec Bundle"}
          </button>
          <button className="secondary-button" disabled type="button">
            Validate Spec (준비중)
          </button>
          <button className="secondary-button" disabled type="button">
            Compile Prompts (준비중)
          </button>
        </div>
      </form>
      {mutation.isError ? (
        <p className="error-text">{mutation.error instanceof Error ? mutation.error.message : "run failed"}</p>
      ) : null}
      <div className="placeholder-grid">
        <article className="placeholder-card">
          <div className="placeholder-card__header">
            <h4>Future Quality Gates</h4>
            <StatusBadge label="준비중" tone="warning" />
          </div>
          <ul>
            <li>Schema alignment (준비중)</li>
            <li>Prompt drift detection (준비중)</li>
            <li>Agent memory snapshot (준비중)</li>
            <li>Policy compliance gate (준비중)</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
