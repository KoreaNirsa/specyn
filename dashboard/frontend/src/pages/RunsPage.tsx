import { PageIntro } from "../components/PageIntro";
import { ResultTimeline } from "../components/ResultTimeline";
import { RunHistoryTable } from "../components/RunHistoryTable";

export function RunsPage() {
  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow="History"
        title="Runs"
        description="최근 로컬 실행 이력과 최신 실행 결과 타임라인을 분리해서 보여줍니다. 자세한 로그 스트리밍과 prompt diff는 추후 연결 예정입니다."
      />
      <div className="split-layout">
        <RunHistoryTable />
        <ResultTimeline />
      </div>
      <section className="split-layout">
        <article className="panel placeholder-card"><h3>Live Logs (준비중)</h3><p className="panel-copy">실시간 토큰/에이전트 로그 패널이 들어갈 영역입니다.</p></article>
        <article className="panel placeholder-card"><h3>Prompt Preview (준비중)</h3><p className="panel-copy">에이전트별 프롬프트 스냅샷 미리보기가 들어갈 영역입니다.</p></article>
        <article className="panel placeholder-card"><h3>Generated Files (준비중)</h3><p className="panel-copy">변경 파일 트리와 diff 요약이 들어갈 영역입니다.</p></article>
      </section>
    </div>
  );
}
