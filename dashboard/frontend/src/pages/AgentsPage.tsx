import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";

const cards = [
  { title: "Planner", items: ["현재 작업 내용 (준비중)", "최근 상태 변경 기록 (준비중)", "에이전트별 SLA / 소요 시간 (준비중)"] },
  { title: "Backend / Frontend", items: ["작업 큐 (준비중)", "handoff trace (준비중)", "미해결 blocker (준비중)"] },
  { title: "Review / Docs", items: ["품질 게이트 현황 (준비중)", "문서 동기화 이력 (준비중)", "릴리즈 승인 상태 (준비중)"] },
];

export function AgentsPage() {
  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="Future Control Plane"
        title="Agents"
        description="앞으로 적용 예정인 에이전트 작업 내용, 상태, 작업 기록을 확인하기 위한 페이지입니다. 현재는 이동 가능한 placeholder 화면만 제공합니다."
        actions={<StatusBadge label="준비중" tone="warning" />}
      />
      <section className="triple-grid">
        {cards.map((card) => (
          <article className="panel placeholder-card" key={card.title}>
            <div className="placeholder-card__header">
              <h3>{card.title}</h3>
              <StatusBadge label="준비중" tone="warning" />
            </div>
            <ul>
              {card.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </div>
  );
}
