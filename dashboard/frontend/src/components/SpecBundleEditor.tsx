import { useWorkspaceStore } from "../store/workspaceStore";
import { useI18n } from "../i18n";
import { SpecType } from "../types";

const ORDER: SpecType[] = ["product", "api", "test", "review", "agent"];

/**
 * Handle spec bundle editor for the current workflow.
 */
export function SpecBundleEditor() {
  const { t } = useI18n();
  const documents = useWorkspaceStore((state) => state.documents);
  const setDocument = useWorkspaceStore((state) => state.setDocument);
  const resetDocuments = useWorkspaceStore((state) => state.resetDocuments);
  const labels: Record<SpecType, string> = {
    product: t("editor.product"),
    api: t("editor.api"),
    test: t("editor.test"),
    review: t("editor.review"),
    agent: t("editor.agent"),
  };

  return (
    <section className="panel editor-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">{t("editor.eyebrow")}</p>
          <h3>{t("editor.title")}</h3>
        </div>
        <button className="ghost-button" type="button" onClick={resetDocuments}>
          {t("editor.reset")}
        </button>
      </div>
      <div className="editor-grid">
        {ORDER.map((type) => (
          <article className="editor-card" key={type}>
            <div className="editor-card__header">
              <strong>{labels[type]}</strong>
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
