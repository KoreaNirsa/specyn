import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";
import { useAiServerHealth, useBackendHealth } from "../hooks/useHealth";
import { useI18n } from "../i18n";

/**
 * Handle system page for the current workflow.
 */
export function SystemPage() {
  const { t } = useI18n();
  const backend = useBackendHealth();
  const aiServer = useAiServerHealth();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("system.eyebrow")}
        title={t("system.title")}
        description={t("system.description")}
      />
      <section className="split-layout">
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>{t("system.dashboardBackend")}</h3>
            <StatusBadge
              label={backend.isError ? t("common.status.down") : backend.data?.status ?? t("common.status.checking")}
              tone={backend.isError ? "danger" : "success"}
            />
          </div>
          <p className="panel-copy">{t("system.backendPort")}</p>
        </article>
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>{t("system.dashboardAi")}</h3>
            <StatusBadge
              label={aiServer.isError ? t("common.status.down") : aiServer.data?.status ?? t("common.status.checking")}
              tone={aiServer.isError ? "danger" : "success"}
            />
          </div>
          <p className="panel-copy">{t("system.aiPort")}</p>
        </article>
        <article className="panel">
          <div className="placeholder-card__header">
            <h3>{t("system.observability")}</h3>
            <StatusBadge label={t("common.status.planned")} tone="warning" />
          </div>
          <p className="panel-copy">{t("system.observabilityCopy")}</p>
        </article>
      </section>
      <section className="triple-grid">
        <article className="panel placeholder-card"><h3>{t("system.errors")}</h3><p className="panel-copy">{t("system.errorsCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("system.locks")}</h3><p className="panel-copy">{t("system.locksCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("system.network")}</h3><p className="panel-copy">{t("system.networkCopy")}</p></article>
      </section>
    </div>
  );
}
