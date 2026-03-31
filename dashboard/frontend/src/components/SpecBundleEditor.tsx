import { useWorkspaceStore } from "../store/workspaceStore";
import { SpecType } from "../types";

const LABELS: Record<SpecType, string> = {
  product: "Product",
  api: "API",
  test: "Test",
  review: "Review",
  agent: "Agent",
};

const ORDER: SpecType[] = ["product", "api", "test", "review", "agent"];

export function SpecBundleEditor() {
  const documents = useWorkspaceStore((state) => state.documents);
  const setDocument = useWorkspaceStore((state) => state.setDocument);
  const resetDocuments = useWorkspaceStore((state) => state.resetDocuments);

  return (
    <section className="panel editor-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Workspace</p>
          <h3>Spec Bundle Editor</h3>
        </div>
        <button className="ghost-button" type="button" onClick={resetDocuments}>
          Reset Docs
        </button>
      </div>
      <div className="editor-grid">
        {ORDER.map((type) => (
          <article className="editor-card" key={type}>
            <div className="editor-card__header">
              <strong>{LABELS[type]}</strong>
              <span>{type}.md</span>
            </div>
            <textarea
              value={documents[type]}
              onChange={(event) => setDocument(type, event.target.value)}
              rows={18}
            />
          </article>
        ))}
      </div>
    </section>
  );
}
