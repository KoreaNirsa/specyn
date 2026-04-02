import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";
import { useI18n } from "../i18n";

/**
 * Handle projects page for the current workflow.
 */
export function ProjectsPage() {
  const { t } = useI18n();

  const projects = [
    {
      name: "sample-service",
      summary: t("projects.sampleSummary"),
      frontend: "http://localhost:5173",
      backend: "http://localhost:8080",
      aiServer: "http://localhost:8000",
      active: true,
    },
    {
      name: "future-project-template",
      summary: t("projects.futureSummary"),
      frontend: `(${t("common.status.planned")})`,
      backend: `(${t("common.status.planned")})`,
      aiServer: `(${t("common.status.planned")})`,
      active: false,
    },
  ];

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("projects.eyebrow")}
        title={t("projects.title")}
        description={t("projects.description")}
      />
      <section className="stack-list">
        {projects.map((project) => (
          <article className="panel project-card" key={project.name}>
            <div className="placeholder-card__header">
              <div>
                <h3>{project.name}</h3>
                <p className="panel-copy">{project.summary}</p>
              </div>
              <StatusBadge
                label={project.active ? t("common.status.active") : t("common.status.planned")}
                tone={project.active ? "success" : "warning"}
              />
            </div>
            <div className="mini-grid">
              <article className="mini-card"><strong>Frontend</strong><span>{project.frontend}</span></article>
              <article className="mini-card"><strong>Backend</strong><span>{project.backend}</span></article>
              <article className="mini-card"><strong>AI Server</strong><span>{project.aiServer}</span></article>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
