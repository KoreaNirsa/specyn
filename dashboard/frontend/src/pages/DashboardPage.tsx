import { MetricCard } from "../components/MetricCard";
import { PageIntro } from "../components/PageIntro";
import { RunHistoryTable } from "../components/RunHistoryTable";
import { SampleRuntimePanel } from "../components/SampleRuntimePanel";
import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { useI18n } from "../i18n";
import { useWorkspaceStore } from "../store/workspaceStore";

/**
 * Handle dashboard page for the current workflow.
 */
export function DashboardPage() {
  const { t } = useI18n();
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();
  const runHistory = useWorkspaceStore((state) => state.runHistory);
  const documents = useWorkspaceStore((state) => state.documents);

  const totalChars = Object.values(documents).reduce((acc, value) => acc + value.length, 0);

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("dashboard.eyebrow")}
        title={t("dashboard.title")}
        description={t("dashboard.description")}
      />
      <section className="metric-grid">
        <MetricCard
          eyebrow={t("dashboard.backendHealth")}
          title={t("dashboard.apiHealth")}
          value={backend.data?.status ?? t("common.status.checking")}
          detail={t("dashboard.orchestratorStatus")}
          badge={{
            label: backend.isError ? t("common.status.down") : backend.data?.status ?? t("common.status.checking"),
            tone: backend.isError ? "danger" : "success",
          }}
        />
        <MetricCard
          eyebrow={t("dashboard.aiHealth")}
          title={t("dashboard.inferenceHealth")}
          value={aiServer.data?.status ?? t("common.status.checking")}
          detail={t("dashboard.aiStatus")}
          badge={{
            label: aiServer.isError ? t("common.status.down") : aiServer.data?.status ?? t("common.status.checking"),
            tone: aiServer.isError ? "danger" : "success",
          }}
        />
        <MetricCard
          eyebrow={t("dashboard.step1")}
          title={t("dashboard.specBundleSize")}
          value={`${totalChars.toLocaleString()} chars`}
          detail={t("dashboard.specBundleDetail")}
          badge={{ label: t("common.status.active"), tone: "success" }}
        />
        <MetricCard
          eyebrow={t("common.output")}
          title={t("dashboard.outputProject")}
          value="sample-service"
          detail={t("dashboard.outputDetail")}
          badge={{ label: t("common.status.fixed"), tone: "warning" }}
        />
      </section>
      <SampleRuntimePanel />
      <div className="split-layout">
        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">{t("dashboard.runtimeMap")}</p>
              <h3>{t("dashboard.runtimeMapTitle")}</h3>
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
              <p className="panel-eyebrow">{t("dashboard.executionOrder")}</p>
              <h3>{t("dashboard.executionOrderTitle")}</h3>
            </div>
          </div>
          <p className="panel-copy">{t("dashboard.order1")}</p>
          <p className="panel-copy">{t("dashboard.order2")}</p>
          <p className="panel-copy">{t("dashboard.order3")}</p>
          <p className="panel-copy">{t("dashboard.runCount", { count: runHistory.length })}</p>
        </section>
      </div>
      <RunHistoryTable />
    </div>
  );
}
