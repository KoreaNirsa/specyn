export function HomePage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h2>프로젝트 소개</h2>
        <p>
          Specyn은 도메인에 종속되지 않는 오픈소스 AX Builder 프레임워크입니다.
          Spec Driven Development, Multi-Agent 협업, Codex 기반 코드 생성을
          처음부터 직접 조립하지 않아도 되도록 설계했습니다.
        </p>
        <p>
          기획 → API/구현 → 테스트 → 리뷰 → 문서화 → 최종 승인까지 이어지는
          production-oriented 흐름을 바로 실험하고 확장할 수 있습니다.
          또한 bounded feedback loop와 구조 규칙(`global/common/domain`)까지 함께 검증할 수 있습니다.
        </p>
      </article>

      <article className="panel">
        <h2>권장 시작 순서</h2>
        <ol>
          <li><code>cp .env.example .env</code> 또는 <code>Copy-Item .env.example .env</code></li>
          <li><code>bootstrap</code></li>
          <li><code>doctor</code></li>
          <li><code>validate-spec</code></li>
          <li><code>compile-prompts</code></li>
          <li><code>run-sim</code>으로 기본 흐름 확인</li>
          <li><code>doctor</code>에서 준비가 확인되면 <code>dev</code></li>
        </ol>
      </article>

      <article className="panel">
        <h2>기본 Agent 카탈로그</h2>
        <ul>
          <li>Planner / Design / API / Backend / Frontend / DBA / DevOps</li>
          <li>Test / Code Analysis / Security / Performance</li>
          <li>Review / Docs / Final Review / RAG(optional)</li>
          <li>필요 시 API↔Backend, Design↔Frontend 같은 bounded feedback loop 구성</li>
        </ul>
      </article>
    </section>
  );
}
