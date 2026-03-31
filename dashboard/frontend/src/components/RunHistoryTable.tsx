import { useWorkspaceStore } from "../store/workspaceStore";

export function RunHistoryTable() {
  const runHistory = useWorkspaceStore((state) => state.runHistory);

  return (
    <section className="panel history-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">Run History</p>
          <h3>Recent Local Sessions</h3>
        </div>
      </div>
      {runHistory.length === 0 ? (
        <p className="empty-text">저장된 실행 기록이 없습니다.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Project</th>
                <th>Status</th>
                <th>Results</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {runHistory.map((entry) => (
                <tr key={entry.runId}>
                  <td>{entry.runId}</td>
                  <td>{entry.projectId}</td>
                  <td>{entry.status}</td>
                  <td>{entry.resultCount}</td>
                  <td>{new Date(entry.createdAt).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
