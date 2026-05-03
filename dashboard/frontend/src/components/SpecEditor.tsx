import { useWorkspaceStore } from "../store/workspaceStore";
import { SPEC_FILE_NAMES, SPEC_ORDER } from "../lib/specKit";

/**
 * Handle spec editor for the current workflow.
 */
export function SpecEditor() {
  const documents = useWorkspaceStore((state) => state.documents);
  const setDocument = useWorkspaceStore((state) => state.setDocument);
  const resetDocuments = useWorkspaceStore((state) => state.resetDocuments);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Spec Editor</h2>
          <p>모든 실행은 Markdown spec bundle을 기준으로 동작합니다.</p>
        </div>
        <button type="button" className="secondary-button" onClick={resetDocuments}>
          예제 복원
        </button>
      </div>
      {SPEC_ORDER.map((type) => (
        <section className="spec-card" key={type}>
          <h3>{SPEC_FILE_NAMES[type]}</h3>
          <textarea
            value={documents[type]}
            onChange={(event) => setDocument(type, event.target.value)}
            rows={16}
          />
        </section>
      ))}
    </section>
  );
}
