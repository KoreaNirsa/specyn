import { MetricCard } from "../components/MetricCard";
import { PageIntro } from "../components/PageIntro";
import { ResultTimeline } from "../components/ResultTimeline";
import { RunControls } from "../components/RunControls";
import { SpecBundleEditor } from "../components/SpecBundleEditor";
import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { useI18n } from "../i18n";

/**
 * Handle workspace page for the current workflow.
 */
export function WorkspacePage() {
  const { t } = useI18n();
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("workspace.eyebrow")}
        title={t("workspace.title")}
        description="Edit specs, run agents, and inspect live agent messages from this workspace."
      />
      <section className="metric-grid">
        <MetricCard
          eyebrow={t("dashboard.backendHealth")}
          title={t("dashboard.apiHealth")}
          value={backend.data?.status ?? t("common.status.checking")}
          detail="/api/v1/spec-runs/health"
          badge={{
            label: backend.isError ? t("common.status.down") : backend.data?.status ?? t("common.status.checking"),
            tone: backend.isError ? "danger" : "success",
          }}
        />
        <MetricCard
          eyebrow={t("dashboard.aiHealth")}
          title="/health"
          value={aiServer.data?.status ?? t("common.status.checking")}
          detail="Dashboard AI server status"
          badge={{
            label: aiServer.isError ? t("common.status.down") : aiServer.data?.status ?? t("common.status.checking"),
            tone: aiServer.isError ? "danger" : "success",
          }}
        />
      </section>
      <SpecBundleEditor />
      <RunControls />
      <ResultTimeline />
    </div>
  );
}
