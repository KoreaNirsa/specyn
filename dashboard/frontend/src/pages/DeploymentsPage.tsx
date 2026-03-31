import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";

export function DeploymentsPage() {
  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Future Delivery Ops"
        title="CI & Deploy"
        description="추후 CI 배포 현황을 붙이기 쉽도록 메뉴와 카드 레이아웃만 먼저 구성했습니다. 실제 데이터 연동 전까지는 준비중 상태를 유지합니다."
        actions={<StatusBadge label="준비중" tone="warning" />}
      />
      <section className="triple-grid">
        <article className="panel placeholder-card"><h3>Pipeline Health (준비중)</h3><p className="panel-copy">build/test/deploy pipeline 상태가 표시될 예정입니다.</p></article>
        <article className="panel placeholder-card"><h3>Environment Promotion (준비중)</h3><p className="panel-copy">dev → staging → prod 승격 상태가 들어갈 예정입니다.</p></article>
        <article className="panel placeholder-card"><h3>Release Notes (준비중)</h3><p className="panel-copy">최근 배포 설명과 릴리즈 노트가 연결될 영역입니다.</p></article>
      </section>
      <section className="split-layout">
        <article className="panel placeholder-card"><h3>Lock Management (준비중)</h3><p className="panel-copy">배포 락과 병렬 승인 관리 카드가 들어갈 자리입니다.</p></article>
        <article className="panel placeholder-card"><h3>Rollout Progress (준비중)</h3><p className="panel-copy">배포율, 오류율, rollback 상태를 표시할 예정입니다.</p></article>
      </section>
    </div>
  );
}
