import { useWorkspaceStore } from "../store/workspaceStore";
import { SPEC_DOCUMENT_LABELS, SPEC_FILE_NAMES, SPEC_ORDER } from "../lib/specKit";
import { useI18n } from "../i18n";

/**
 * Handle spec bundle editor for the current workflow.
 */
export function SpecBundleEditor() {
  const { t } = useI18n();
  const documents = useWorkspaceStore((state) => state.documents);
  const setDocument = useWorkspaceStore((state) => state.setDocument);
  const resetDocuments = useWorkspaceStore((state) => state.resetDocuments);

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
        {SPEC_ORDER.map((type) => (
          <article className="editor-card" key={type}>
            <div className="editor-card__header">
              <strong>{SPEC_DOCUMENT_LABELS[type]}</strong>
              <span>{SPEC_FILE_NAMES[type]}</span>
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
