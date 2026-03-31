import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { MetricCard } from "../components/MetricCard";
import { PageIntro } from "../components/PageIntro";
import { ResultTimeline } from "../components/ResultTimeline";
import { RunControls } from "../components/RunControls";
import { SpecBundleEditor } from "../components/SpecBundleEditor";

export function WorkspacePage() {
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Run Studio"
        title="Workspace"
        description="현재 Specyn에 이미 구현된 spec 편집, health 확인, spec-run 실행 기능을 관리자형 워크스페이스 화면으로 묶었습니다."
      />
      <section className="metric-grid">
        <MetricCard
          eyebrow="Backend"
          title="Spec Run API"
          value={backend.data?.status ?? "CHECKING"}
          detail="/api/v1/spec-runs/health 응답 상태"
          badge={{ label: backend.isError ? "DOWN" : backend.data?.status ?? "PENDING", tone: backend.isError ? "danger" : "success" }}
        />
        <MetricCard
          eyebrow="AI Server"
          title="/health"
          value={aiServer.data?.status ?? "CHECKING"}
          detail="대시보드 AI server 상태"
          badge={{ label: aiServer.isError ? "DOWN" : aiServer.data?.status ?? "PENDING", tone: aiServer.isError ? "danger" : "success" }}
        />
      </section>
      <RunControls />
      <SpecBundleEditor />
      <ResultTimeline />
    </div>
  );
}
