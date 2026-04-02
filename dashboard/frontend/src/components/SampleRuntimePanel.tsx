import { useQuery } from "@tanstack/react-query";

import {
  fetchSampleAiServerHealth,
  fetchSampleBackendHealth,
  fetchSampleBackendSummary,
} from "../api/client";
import { useI18n } from "../i18n";
import { useWorkspaceStore } from "../store/workspaceStore";
import { StatusBadge } from "./StatusBadge";

function useSampleBackendRuntimeHealth() {
  return useQuery({
    queryKey: ["sample-backend-health"],
    queryFn: fetchSampleBackendHealth,
    refetchInterval: 10000,
    retry: false,
  });
}

function useSampleAiRuntimeHealth() {
  return useQuery({
    queryKey: ["sample-ai-health"],
    queryFn: fetchSampleAiServerHealth,
    refetchInterval: 10000,
    retry: false,
  });
}

function useSampleGeneratedSummary() {
  return useQuery({
    queryKey: ["sample-generated-summary"],
    queryFn: fetchSampleBackendSummary,
    refetchInterval: 10000,
    retry: false,
  });
}

/**
 * Handle sample runtime panel for the current workflow.
 */
export function SampleRuntimePanel() {
  const { t } = useI18n();
  const results = useWorkspaceStore((state) => state.results);
  const backend = useSampleBackendRuntimeHealth();
  const aiServer = useSampleAiRuntimeHealth();
  const summary = useSampleGeneratedSummary();

  const hasGeneratedOutput = results.length > 0;

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">{t("runtime.eyebrow")}</p>
          <h3>{t("runtime.title")}</h3>
        </div>
      </div>
      <p className="panel-copy">{t("runtime.description")}</p>
      <div className="mini-grid">
        <article className="mini-card">
          <strong>{t("runtime.generatedOutput")}</strong>
          <span>{hasGeneratedOutput ? t("common.status.ready") : t("common.status.waiting")}</span>
        </article>
        <article className="mini-card">
          <strong>{t("runtime.backendHealth")}</strong>
          <span>
            {backend.isError ? t("common.status.down") : backend.data?.status ?? t("common.status.checking")}
          </span>
        </article>
        <article className="mini-card">
          <strong>{t("runtime.aiHealth")}</strong>
          <span>
            {aiServer.isError ? t("common.status.down") : aiServer.data?.status ?? t("common.status.checking")}
          </span>
        </article>
        <article className="mini-card">
          <strong>{t("runtime.generatedSummary")}</strong>
          <span>{summary.isError ? t("common.status.down") : t("common.status.ready")}</span>
        </article>
      </div>
      <div className="placeholder-grid">
        <article className="placeholder-card">
          <div className="placeholder-card__header">
            <h4>{t("runtime.links")}</h4>
            <StatusBadge
              label={hasGeneratedOutput ? t("common.status.generated") : t("common.status.waiting")}
              tone={hasGeneratedOutput ? "success" : "warning"}
            />
          </div>
          <ul>
            <li>
              <a href="http://localhost:5173" rel="noreferrer" target="_blank">
                {t("runtime.openFrontend")}
              </a>
            </li>
            <li>
              <a href="http://localhost:8080/actuator/health" rel="noreferrer" target="_blank">
                {t("runtime.openBackendHealth")}
              </a>
            </li>
            <li>
              <a
                href="http://localhost:8080/api/v1/generated/sample-service/summary"
                rel="noreferrer"
                target="_blank"
              >
                {t("runtime.openSummary")}
              </a>
            </li>
            <li>
              <a href="http://localhost:8000/health" rel="noreferrer" target="_blank">
                {t("runtime.openAiHealth")}
              </a>
            </li>
            <li>
              <a
                href="http://localhost:8000/generated/sample-service/context"
                rel="noreferrer"
                target="_blank"
              >
                {t("runtime.openContext")}
              </a>
            </li>
          </ul>
        </article>
        <article className="placeholder-card">
          <div className="placeholder-card__header">
            <h4>{t("runtime.nextCommand")}</h4>
            <StatusBadge label={t("common.status.manual")} tone="warning" />
          </div>
          <p className="panel-copy">{t("runtime.nextCommandCopy")}</p>
          <pre>python specyn.py sample-up -d</pre>
        </article>
      </div>
    </section>
  );
}
