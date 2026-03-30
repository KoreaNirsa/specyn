export function HomePage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h2>프로젝트 소개</h2>
        <p>
          Specyn은 spec bundle → prompt → multi-agent flow → generated code → 실행 확인까지
          이어지는 SDD(Spec Driven Development) 프레임워크입니다.
        </p>
        <p>
          현재 저장소에는 <code>specs/projects/sample-service</code> 라는 reference sample이 포함되어 있으며,
          <code>specyn.py run</code> 이후 실제 Task CRUD 웹사이트를 바로 확인할 수 있습니다.
        </p>
      </article>

      <article className="panel">
        <h2>가장 추천하는 시작 순서</h2>
        <ol>
          <li><code>Copy-Item .env.example .env</code> 또는 <code>cp .env.example .env</code></li>
          <li><code>python scripts/specyn_tasks.py bootstrap</code></li>
          <li><code>python scripts/specyn_tasks.py doctor</code></li>
          <li><code>python specyn.py validate --spec-dir specs/projects/sample-service</code></li>
          <li><code>python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service</code></li>
          <li><code>python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service</code></li>
          <li><code>python scripts/specyn_tasks.py dev</code></li>
        </ol>
      </article>

      <article className="panel">
        <h2>sample-service 에서 확인할 것</h2>
        <ul className="stack-list">
          <li><code>/generated/sample-service</code> 에서 generated CRUD 페이지 확인</li>
          <li>작업 생성 / 상세 조회 / 상태 토글 / 삭제</li>
          <li><code>/api/v1/tasks</code> 와 <code>/api/v1/generated/sample-service/summary</code> 확인</li>
          <li><code>/generated/sample-service/context</code> 로 AI Server context 확인</li>
        </ul>
      </article>

      <article className="panel">
        <h2>실행 모드</h2>
        <ul className="stack-list">
          <li>로컬 CLI 런타임: deterministic generated 산출물 생성</li>
          <li>Codex 실행 환경: Backend + AI Server + Codex CLI 경유 patch/file 생성</li>
          <li><code>agent.md</code> 에서 execution flow 와 feedback loop 를 제어</li>
        </ul>
      </article>
    </section>
  );
}
