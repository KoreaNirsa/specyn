import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";

const projects = [
  {
    name: "sample-service",
    summary: "현재 specyn run 으로 생성/검증 가능한 reference sample 프로젝트",
    frontend: "http://localhost:5173",
    backend: "http://localhost:8080",
    aiServer: "http://localhost:8000",
  },
  {
    name: "future-project-template",
    summary: "새 스펙으로 생성될 프로젝트 런타임 자리",
    frontend: "(준비중)",
    backend: "(준비중)",
    aiServer: "(준비중)",
  },
];

export function ProjectsPage() {
  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Project Runtime"
        title="Projects"
        description="Specyn 대시보드와 분리된 실제 프로젝트 런타임 목록입니다. sample-service는 현재 확인 가능하고, 이후 생성될 프로젝트를 위한 카드도 미리 준비했습니다."
      />
      <section className="stack-list">
        {projects.map((project) => (
          <article className="panel project-card" key={project.name}>
            <div className="placeholder-card__header">
              <div>
                <h3>{project.name}</h3>
                <p className="panel-copy">{project.summary}</p>
              </div>
              <StatusBadge label={project.name === "sample-service" ? "ACTIVE" : "준비중"} tone={project.name === "sample-service" ? "success" : "warning"} />
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
