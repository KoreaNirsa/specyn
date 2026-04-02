import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";
import { useI18n } from "../i18n";

/**
 * Handle deployments page for the current workflow.
 */
export function DeploymentsPage() {
  const { t } = useI18n();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("deploy.eyebrow")}
        title={t("deploy.title")}
        description={t("deploy.description")}
        actions={<StatusBadge label={t("common.status.planned")} tone="warning" />}
      />
      <section className="triple-grid">
        <article className="panel placeholder-card"><h3>{t("deploy.pipeline")}</h3><p className="panel-copy">{t("deploy.pipelineCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("deploy.env")}</h3><p className="panel-copy">{t("deploy.envCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("deploy.release")}</h3><p className="panel-copy">{t("deploy.releaseCopy")}</p></article>
      </section>
      <section className="split-layout">
        <article className="panel placeholder-card"><h3>{t("deploy.lock")}</h3><p className="panel-copy">{t("deploy.lockCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("deploy.rollout")}</h3><p className="panel-copy">{t("deploy.rolloutCopy")}</p></article>
      </section>
    </div>
  );
}
