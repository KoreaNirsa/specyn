import { PageIntro } from "../components/PageIntro";
import { ResultTimeline } from "../components/ResultTimeline";
import { RunHistoryTable } from "../components/RunHistoryTable";
import { useI18n } from "../i18n";

/**
 * Handle runs page for the current workflow.
 */
export function RunsPage() {
  const { t } = useI18n();

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("runs.eyebrow")}
        title={t("runs.title")}
        description={t("runs.description")}
      />
      <div className="split-layout">
        <RunHistoryTable />
        <ResultTimeline />
      </div>
      <section className="split-layout">
        <article className="panel placeholder-card"><h3>{t("runs.logs")}</h3><p className="panel-copy">{t("runs.logsCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("runs.promptPreview")}</h3><p className="panel-copy">{t("runs.promptCopy")}</p></article>
        <article className="panel placeholder-card"><h3>{t("runs.generatedFiles")}</h3><p className="panel-copy">{t("runs.filesCopy")}</p></article>
      </section>
    </div>
  );
}
