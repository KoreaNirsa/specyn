import GeneratedProjectPage from "./generated/sample-service/GeneratedProjectPage";

export default function App() {
  return (
    <div className="layout">
      <header className="topbar">
        <div>
          <p className="eyebrow">Generated Project Runtime</p>
          <h1>sample-service</h1>
          <p className="muted-text">
            Specyn 대시보드와 분리된 실제 프로젝트 런타임입니다. frontend/backend/ai-server 가
            projects/sample-service 아래에 독립 배치되어 있습니다.
          </p>
        </div>
        <div className="button-row">
          <a
            className="link-button"
            href="http://localhost:8080/api/v1/generated/sample-service/summary"
            rel="noreferrer"
            target="_blank"
          >
            Backend Summary
          </a>
          <a
            className="link-button secondary-link-button"
            href="http://localhost:8000/generated/sample-service/context"
            rel="noreferrer"
            target="_blank"
          >
            AI Context
          </a>
        </div>
      </header>
      <GeneratedProjectPage />
    </div>
  );
}
