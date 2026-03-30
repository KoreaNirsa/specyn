import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";

function HealthCard(props: {
  title: string;
  statusLabel: string;
  description: string;
}) {
  return (
    <article className="health-card">
      <h3>{props.title}</h3>
      <p><strong>상태:</strong> {props.statusLabel}</p>
      <p>{props.description}</p>
    </article>
  );
}

export function HealthPanel() {
  const backendHealth = useBackendHealth();
  const aiServerHealth = useAiServerHealth();

  return (
    <section className="panel">
      <h2>플랫폼 상태</h2>
      <div className="health-grid">
        <HealthCard
          title="Backend"
          statusLabel={backendHealth.data?.status ?? (backendHealth.isError ? "DOWN" : "CHECKING")}
          description="Spec 수신, 실행 순서 결정, 결과 집계를 담당합니다."
        />
        <HealthCard
          title="AI Server"
          statusLabel={aiServerHealth.data?.status ?? (aiServerHealth.isError ? "DOWN" : "CHECKING")}
          description={`모델=${aiServerHealth.data?.model ?? "-"}, codex=${aiServerHealth.data?.codexMode ?? "-"}`}
        />
      </div>
    </section>
  );
}
