import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { useWorkspaceStore } from "../store/workspaceStore";
import { MetricCard } from "../components/MetricCard";
import { PageIntro } from "../components/PageIntro";
import { RunHistoryTable } from "../components/RunHistoryTable";

export function DashboardPage() {
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();
  const runHistory = useWorkspaceStore((state) => state.runHistory);
  const documents = useWorkspaceStore((state) => state.documents);

  const totalChars = Object.values(documents).reduce((acc, value) => acc + value.length, 0);

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Overview"
        title="Specyn Dashboard Summary"
        description="stitch 샘플의 카드형 운영 대시보드 레이아웃을 참고해, 현재 구현된 Specyn 기능을 관리자형 화면으로 재배치했습니다. 모든 페이지는 동일한 AppShell 레이아웃을 공유합니다."
      />
      <section className="metric-grid">
        <MetricCard
          eyebrow="Dashboard Backend"
          title="API Health"
          value={backend.data?.status ?? "CHECKING"}
          detail="현재 spec-runs orchestrator 상태를 표시합니다."
          badge={{ label: backend.isError ? "DOWN" : backend.data?.status ?? "PENDING", tone: backend.isError ? "danger" : "success" }}
        />
        <MetricCard
          eyebrow="Dashboard AI Server"
          title="Inference Health"
          value={aiServer.data?.status ?? "CHECKING"}
          detail="대시보드 AI server의 기본 헬스 상태입니다."
          badge={{ label: aiServer.isError ? "DOWN" : aiServer.data?.status ?? "PENDING", tone: aiServer.isError ? "danger" : "success" }}
        />
        <MetricCard
          eyebrow="Workspace"
          title="Spec Bundle Size"
          value={`${totalChars.toLocaleString()} chars`}
          detail="현재 저장된 editor 문서 길이 합계입니다."
          badge={{ label: "ACTIVE", tone: "success" }}
        />
        <MetricCard
          eyebrow="Future Modules"
          title="Agent / CI Slots"
          value="4"
          detail="에이전트 관리, 배포 현황, 로그, 롤아웃 보드가 준비되어 있습니다."
          badge={{ label: "준비중", tone: "warning" }}
        />
      </section>
      <div className="split-layout">
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Live Runtime Map</p>
              <h3>Separated Local Ports</h3>
            </div>
          </div>
          <div className="mini-grid">
            <article className="mini-card"><strong>Dashboard Frontend</strong><span>http://localhost:4173</span></article>
            <article className="mini-card"><strong>Dashboard Backend</strong><span>http://localhost:8180</span></article>
            <article className="mini-card"><strong>Dashboard AI Server</strong><span>http://localhost:8100</span></article>
            <article className="mini-card"><strong>sample-service Frontend</strong><span>http://localhost:5173</span></article>
            <article className="mini-card"><strong>sample-service Backend</strong><span>http://localhost:8080</span></article>
            <article className="mini-card"><strong>sample-service AI Server</strong><span>http://localhost:8000</span></article>
          </div>
        </section>
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Recent Activity</p>
              <h3>Run Snapshot</h3>
            </div>
          </div>
          <p className="panel-copy">최근 저장된 세션 수: {runHistory.length}</p>
          <p className="panel-copy">현재는 이미 구현된 실행/헬스 확인 기능만 연결했고, Agent 관리와 CI 보드는 하드코딩 placeholder입니다.</p>
        </section>
      </div>
      <RunHistoryTable />
    </div>
  );
}
