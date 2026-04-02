import { useWorkspaceStore } from "../store/workspaceStore";
import { useI18n } from "../i18n";

/**
 * Run history table for the current workflow.
 */
export function RunHistoryTable() {
  const { t, language } = useI18n();
  const runHistory = useWorkspaceStore((state) => state.runHistory);

  return (
    <section className="panel history-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">{t("history.eyebrow")}</p>
          <h3>{t("history.title")}</h3>
        </div>
      </div>
      {runHistory.length === 0 ? (
        <p className="empty-text">{t("history.empty")}</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("history.runId")}</th>
                <th>{t("history.project")}</th>
                <th>{t("history.workspace")}</th>
                <th>{t("history.status")}</th>
                <th>{t("history.results")}</th>
                <th>{t("history.created")}</th>
              </tr>
            </thead>
            <tbody>
              {runHistory.map((entry) => (
                <tr key={entry.runId}>
                  <td>{entry.runId}</td>
                  <td>{entry.projectId}</td>
                  <td>{entry.workspacePath}</td>
                  <td>{entry.status}</td>
                  <td>{entry.resultCount}</td>
                  <td>{new Date(entry.createdAt).toLocaleString(language === "ko" ? "ko-KR" : "en-US")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
