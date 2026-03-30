import { FormEvent, useEffect, useState } from "react";

          import { generatedApiContract } from "./apiContract";

          const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8080";
          const SUMMARY_URL = BACKEND_URL + "/api/v1/generated/sample-service/summary";
          const TASKS_URL = BACKEND_URL + "/api/v1/tasks";

          type TaskItem = {
            id: number;
            title: string;
            description?: string;
            status: string;
            createdAt?: string;
            updatedAt?: string;
          };

          type TasksPayload = { items?: TaskItem[] };
          type TaskPayload = { item?: TaskItem };

          const ENDPOINTS = [
            {"method": "GET", "path": "/api/v1/tasks", "description": "작업 목록 조회", "auth": "없음", "note": "seeded task + 생성된 task를 함께 반환"},
{"method": "GET", "path": "/api/v1/tasks/{id}", "description": "작업 단건 조회", "auth": "없음", "note": "존재하지 않으면 404"},
{"method": "POST", "path": "/api/v1/tasks", "description": "작업 생성", "auth": "없음", "note": "`title` 필수"},
{"method": "PATCH", "path": "/api/v1/tasks/{id}/status", "description": "작업 상태 변경", "auth": "없음", "note": "`PENDING`, `DONE` 만 허용"},
{"method": "DELETE", "path": "/api/v1/tasks/{id}", "description": "작업 삭제", "auth": "없음", "note": "성공 시 204"}
          ] as const;

          async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
            const response = await fetch(url, {
              ...init,
              headers: {
                "Content-Type": "application/json",
                ...(init?.headers ?? {}),
              },
            });

            const text = await response.text();
            const payload = text ? JSON.parse(text) : null;
            if (!response.ok) {
              const message =
                payload && typeof payload === "object" && "message" in payload && typeof (payload as { message?: unknown }).message === "string"
                  ? String((payload as { message: string }).message)
                  : `${response.status} ${response.statusText}`;
              throw new Error(message);
            }
            return payload as T;
          }

          async function requestNoContent(url: string, init?: RequestInit): Promise<void> {
            const response = await fetch(url, init);
            if (!response.ok) {
              const text = await response.text();
              const payload = text ? JSON.parse(text) : null;
              const message =
                payload && typeof payload === "object" && "message" in payload && typeof (payload as { message?: unknown }).message === "string"
                  ? String((payload as { message: string }).message)
                  : `${response.status} ${response.statusText}`;
              throw new Error(message);
            }
          }

          function taskDetailUrl(id: number): string {
            return BACKEND_URL + `/api/v1/tasks/${id}`;
          }

          function taskStatusUrl(id: number): string {
            return BACKEND_URL + `/api/v1/tasks/${id}/status`;
          }

          export default function GeneratedProjectPage() {
            const [tasks, setTasks] = useState<TaskItem[]>([]);
            const [summaryPayload, setSummaryPayload] = useState<string>("loading...");
            const [detailPayload, setDetailPayload] = useState<string>("목록에서 '상세 보기'를 누르면 개별 GET 응답을 확인할 수 있습니다.");
            const [title, setTitle] = useState("");
            const [description, setDescription] = useState("");
            const [loading, setLoading] = useState(true);
            const [submitting, setSubmitting] = useState(false);
            const [errorMessage, setErrorMessage] = useState<string | null>(null);
            const [selectedId, setSelectedId] = useState<number | null>(null);

            async function refreshSummary(): Promise<void> {
              const payload = await fetchJson<Record<string, unknown>>(SUMMARY_URL);
              setSummaryPayload(JSON.stringify(payload, null, 2));
            }

            async function refreshTasks(): Promise<TaskItem[]> {
              const payload = await fetchJson<TasksPayload>(TASKS_URL);
              const items = Array.isArray(payload.items) ? payload.items : [];
              setTasks(items);
              return items;
            }

            async function refreshAll(): Promise<void> {
              setLoading(true);
              setErrorMessage(null);
              try {
                await Promise.all([refreshSummary(), refreshTasks()]);
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setErrorMessage(message);
              } finally {
                setLoading(false);
              }
            }

            useEffect(() => {
              void refreshAll();
            }, []);

            async function loadTaskDetail(id: number): Promise<void> {
              const payload = await fetchJson<TaskPayload>(taskDetailUrl(id));
              setSelectedId(id);
              setDetailPayload(JSON.stringify(payload, null, 2));
            }

            async function handleCreate(event: FormEvent<HTMLFormElement>): Promise<void> {
              event.preventDefault();
              setSubmitting(true);
              setErrorMessage(null);
              try {
                const payload = await fetchJson<TaskPayload>(TASKS_URL, {
                  method: "POST",
                  body: JSON.stringify({ title, description }),
                });
                setTitle("");
                setDescription("");
                await refreshSummary();
                await refreshTasks();
                if (payload.item?.id) {
                  await loadTaskDetail(payload.item.id);
                }
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setErrorMessage(message);
              } finally {
                setSubmitting(false);
              }
            }

            async function handleToggleStatus(task: TaskItem): Promise<void> {
              const nextStatus = task.status === "DONE" ? "PENDING" : "DONE";
              setErrorMessage(null);
              try {
                await fetchJson<TaskPayload>(taskStatusUrl(task.id), {
                  method: "PATCH",
                  body: JSON.stringify({ status: nextStatus }),
                });
                await refreshSummary();
                await refreshTasks();
                await loadTaskDetail(task.id);
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setErrorMessage(message);
              }
            }

            async function handleDelete(taskId: number): Promise<void> {
              setErrorMessage(null);
              try {
                await requestNoContent(taskDetailUrl(taskId), { method: "DELETE" });
                const items = await refreshTasks();
                await refreshSummary();
                if (selectedId === taskId) {
                  setSelectedId(null);
                  setDetailPayload("삭제된 항목입니다. 다른 항목을 선택하거나 새 작업을 생성해 보세요.");
                }
                if (items.length === 0) {
                  setDetailPayload("현재 등록된 작업이 없습니다. 위 폼에서 새 작업을 생성해 보세요.");
                }
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setErrorMessage(message);
              }
            }

            return (
              <section className="page-grid">
                <article className="panel">
                  <h2>Sample Service · Generated CRUD Demo</h2>
                  <p>Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.</p>
                  <p>
                    이 페이지는 <code>specyn run</code> 실행으로 생성된 간단한 작업 관리 웹사이트입니다.
                    아래에서 생성, 상세 조회, 상태 변경, 삭제를 모두 확인할 수 있습니다.
                  </p>
                  <ul className="stack-list">
                    {generatedApiContract.scenarios.map((scenario) => (
                      <li key={scenario}>{scenario}</li>
                    ))}
                  </ul>
                </article>

                <article className="panel">
                  <div className="panel-header">
                    <h2>새 작업 생성</h2>
                    <button type="button" className="secondary-button" onClick={() => void refreshAll()} disabled={loading}>
                      새로고침
                    </button>
                  </div>
                  <form className="form-grid" onSubmit={(event) => void handleCreate(event)}>
                    <label>
                      제목
                      <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="예: README 업데이트" />
                    </label>
                    <label>
                      설명
                      <textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="예: generated page와 backend API를 함께 확인한다." />
                    </label>
                    <div className="button-row">
                      <button type="submit" disabled={submitting}>
                        {submitting ? "저장 중..." : "작업 생성"}
                      </button>
                    </div>
                  </form>
                  {errorMessage ? <div className="error-box">{errorMessage}</div> : null}
                </article>

                <article className="panel">
                  <h2>현재 작업 목록</h2>
                  {loading ? <p>작업을 불러오는 중입니다...</p> : null}
                  {!loading && tasks.length === 0 ? <p>아직 등록된 작업이 없습니다.</p> : null}
                  <div className="results-grid">
                    {tasks.map((task) => (
                      <article className="result-card" key={task.id}>
                        <div className="panel-header">
                          <h3>{task.title}</h3>
                          <span className={`status-badge ${task.status === "DONE" ? "status-done" : "status-pending"}`}>
                            {task.status}
                          </span>
                        </div>
                        <p className="muted-text">ID: {task.id}</p>
                        <p>{task.description || "설명이 없습니다."}</p>
                        <div className="button-row">
                          <button type="button" className="secondary-button" onClick={() => void loadTaskDetail(task.id)}>
                            상세 보기
                          </button>
                          <button type="button" onClick={() => void handleToggleStatus(task)}>
                            상태 토글
                          </button>
                          <button type="button" className="secondary-button" onClick={() => void handleDelete(task.id)}>
                            삭제
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                </article>

                <article className="panel">
                  <h2>선택한 작업 상세</h2>
                  <p className="muted-text">
                    {selectedId === null ? "선택된 작업이 없습니다." : `선택된 ID: ${selectedId}`}
                  </p>
                  <pre>{detailPayload}</pre>
                </article>

                <article className="panel">
                  <h2>Generated Summary</h2>
                  <pre>{summaryPayload}</pre>
                </article>

                <article className="panel">
                  <h2>API Contract</h2>
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
