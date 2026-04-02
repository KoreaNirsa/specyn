import { useEffect, useState } from "react";
import type { ComponentType } from "react";
import { useParams } from "react-router-dom";

import { loadGeneratedProjectComponent } from "../lib/generatedPages";

/**
 * Handle generated project route page for the current workflow.
 */
export function GeneratedProjectRoutePage() {
  const { projectId = "" } = useParams();
  const [component, setComponent] = useState<ComponentType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void loadGeneratedProjectComponent(projectId).then((resolved) => {
      if (cancelled) {
        return;
      }
      setComponent(() => resolved);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  if (loading) {
    return (
      <section className="page-grid">
        <article className="panel">
          <p>generated page를 불러오는 중입니다...</p>
        </article>
      </section>
    );
  }

  if (!component) {
    return (
      <section className="page-grid">
        <article className="panel">
          <h2>생성 결과를 찾을 수 없습니다</h2>
          <p>
            먼저 <code>specyn run --spec-dir ...</code> 을 실행해 <code>frontend/src/generated/{projectId}</code>
            산출물을 만드세요.
          </p>
        </article>
      </section>
    );
  }

  const ResolvedComponent = component;
  return <ResolvedComponent />;
}
