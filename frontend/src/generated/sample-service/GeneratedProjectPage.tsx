import { useEffect, useState } from "react";

          import { generatedApiContract } from "./apiContract";

          const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8080";
          const ENDPOINTS = [
            {"method": "GET", "path": "/api/v1/example", "description": "목록 조회", "auth": "없음", "note": ""},
{"method": "POST", "path": "/api/v1/example", "description": "생성", "auth": "없음", "note": ""}
          ] as const;

          export default function GeneratedProjectPage() {
            const [summaryPayload, setSummaryPayload] = useState<string>("loading...");

            useEffect(() => {
              let cancelled = false;
              async function loadSummary() {
                try {
                  const response = await fetch(BACKEND_URL + "/api/v1/generated/sample-service/summary");
                  const payload = await response.json();
                  if (!cancelled) {
                    setSummaryPayload(JSON.stringify(payload, null, 2));
                  }
                } catch (error) {
                  if (!cancelled) {
                    const message = error instanceof Error ? error.message : String(error);
                    setSummaryPayload("failed to load summary: " + message);
                  }
                }
              }
              void loadSummary();
              return () => {
                cancelled = true;
              };
            }, []);

            return (
              <section className="page-grid">
                <article className="panel">
                  <h2>Sample Service · Generated Project Page</h2>
                  <p>이 문서는 서비스의 제품 목표, 사용자 가치, 성공 기준을 정의하고 downstream spec의 기준점을 제공한다.</p>
                  <p>
                    이 페이지는 <code>specyn run --spec-dir ...</code> 실행 시 생성된 산출물입니다.
                    생성된 API contract와 backend summary endpoint를 바로 확인할 수 있습니다.
                  </p>
                </article>

                <article className="panel">
                  <h2>요약</h2>
                  <pre>{summaryPayload}</pre>
                </article>

                <article className="panel">
                  <h2>Endpoint Contract</h2>
                  <pre>{JSON.stringify(generatedApiContract, null, 2)}</pre>
                </article>

                <article className="panel">
                  <h2>Endpoints</h2>
                  <div className="results-grid">
                    {ENDPOINTS.map((endpoint) => (
                      <article className="result-card" key={endpoint.method + "-" + endpoint.path}>
                        <h3>{endpoint.method} {endpoint.path}</h3>
                        <p>{endpoint.description}</p>
                        <p><strong>인증:</strong> {endpoint.auth}</p>
                        <p><strong>비고:</strong> {endpoint.note || "-"}</p>
                      </article>
                    ))}
                  </div>
                </article>
              </section>
            );
          }
