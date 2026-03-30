import { Link } from "react-router-dom";

import { listGeneratedProjectIds } from "../lib/generatedPages";

export function GeneratedProjectsPage() {
  const projectIds = listGeneratedProjectIds();

  return (
    <section className="page-grid">
      <article className="panel">
        <h2>Generated Projects</h2>
        <p>
          <code>specyn run</code> 로 생성된 프런트엔드 프로젝트 페이지를 여기서 확인할 수 있습니다.
        </p>
      </article>

      <article className="panel">
        <h2>목록</h2>
        {projectIds.length === 0 ? (
          <p>아직 생성된 프로젝트 페이지가 없습니다.</p>
        ) : (
          <div className="results-grid">
            {projectIds.map((projectId) => (
              <article className="result-card" key={projectId}>
                <h3>{projectId}</h3>
                <p>
                  <Link to={`/generated/${projectId}`}>생성 결과 보기</Link>
                </p>
              </article>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
