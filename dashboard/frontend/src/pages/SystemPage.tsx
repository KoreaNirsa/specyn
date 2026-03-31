import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";

export function SystemPage() {
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Infrastructure"
        title="System"
        description="stitch의 system/infrastructure 패턴을 참고해 현재 연결 가능한 health 정보와 추후 확장될 운영 카드들을 함께 배치했습니다."
      />
      <section className="split-layout">
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>Dashboard Backend</h3>
            <StatusBadge label={backend.isError ? "DOWN" : backend.data?.status ?? "CHECKING"} tone={backend.isError ? "danger" : "success"} />
          </div>
          <p className="panel-copy">Port 8180 · spec-runs health endpoint</p>
        </article>
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>Dashboard AI Server</h3>
            <StatusBadge label={aiServer.isError ? "DOWN" : aiServer.data?.status ?? "CHECKING"} tone={aiServer.isError ? "danger" : "success"} />
          </div>
          <p className="panel-copy">Port 8100 · FastAPI health endpoint</p>
        </article>
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>Observability</h3>
            <StatusBadge label="준비중" tone="warning" />
          </div>
          <p className="panel-copy">metrics, traces, resource usage는 추후 추가 예정입니다.</p>
        </article>
      </section>
      <section className="triple-grid">
        <article className="panel placeholder-card"><h3>Recent System Errors (준비중)</h3><p className="panel-copy">오류 이벤트와 로그 샘플 영역</p></article>
        <article className="panel placeholder-card"><h3>Resource Locks (준비중)</h3><p className="panel-copy">workspace / deploy 락 상태 영역</p></article>
        <article className="panel placeholder-card"><h3>Network Topology (준비중)</h3><p className="panel-copy">dashboard/project 런타임 연결도 영역</p></article>
      </section>
    </div>
  );
}
