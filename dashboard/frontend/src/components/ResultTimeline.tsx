import { useWorkspaceStore } from "../store/workspaceStore";
import { StatusBadge } from "./StatusBadge";

export function ResultTimeline() {
  const results = useWorkspaceStore((state) => state.results);

  return (
    <section className="panel timeline-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Execution Result</p>
          <h3>Latest Agent Timeline</h3>
        </div>
      </div>
      {results.length === 0 ? (
        <p className="empty-text">아직 실행 결과가 없습니다. Workspace에서 Run Current Spec Bundle을 눌러 주세요.</p>
      ) : (
        <div className="timeline-list">
          {results.map((result, index) => (
            <article className="timeline-item" key={`${result.agent}-${index}`}>
              <div className="timeline-item__top">
                <strong>{result.agent}</strong>
                <StatusBadge
                  label={result.status}
                  tone={result.status === "COMPLETED" ? "success" : result.status === "BLOCKED" ? "danger" : "warning"}
                />
              </div>
              <p className="panel-copy">{result.summary}</p>
              {result.generatedFiles.length > 0 ? (
                <ul className="mini-list">
                  {result.generatedFiles.slice(0, 4).map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
