import { useEffect, useMemo, useRef } from "react";

import { useI18n } from "../i18n";
import { useWorkspaceStore } from "../store/workspaceStore";
import { StatusBadge } from "./StatusBadge";

/**
 * Handle result timeline for the current workflow.
 */
export function ResultTimeline() {
  const { t } = useI18n();
  const results = useWorkspaceStore((state) => state.results);
  const eventTrace = useWorkspaceStore((state) => state.eventTrace);
  const currentRunId = useWorkspaceStore((state) => state.currentRunId);
  const currentWorkspacePath = useWorkspaceStore((state) => state.currentWorkspacePath);
  const conversationRef = useRef<HTMLDivElement | null>(null);

  const timelineState = useMemo(() => {
    const conversations: Array<{
      id: string;
      agent: string;
      stepIndex: number | null;
      text: string;
    }> = [];
    const groups = new Map<
      string,
      {
        key: string;
        agent: string;
        stepIndex: number | null;
        messages: string[];
        logs: string[];
        summary: string;
        status: string;
        latestText: string;
      }
    >();

    for (const event of eventTrace) {
      const agent = event.agent ?? "system";
      const stepKey = `${event.stepIndex ?? 0}-${agent}`;
      const group = groups.get(stepKey) ?? {
        key: stepKey,
        agent,
        stepIndex: event.stepIndex ?? null,
        messages: [],
        logs: [],
        summary: "",
        status: "RUNNING",
        latestText: "",
      };

      if (event.type === "step-start" && event.message) {
        group.logs.push(event.message);
      }

      if (event.type === "step-log" && event.message) {
        group.logs.push(event.message);
        const extractedMessage = extractAgentMessage(event.message);
        if (extractedMessage) {
          group.messages.push(extractedMessage);
          group.latestText = extractedMessage;
          conversations.push({
            id: `${stepKey}-${conversations.length}`,
            agent,
            stepIndex: event.stepIndex ?? null,
            text: extractedMessage,
          });
        }
      }

      if (event.type === "step-complete") {
        group.status = event.status ?? "COMPLETED";
        group.summary = event.summary ?? "";
        if (event.summary) {
          group.logs.push(`[summary] ${event.summary}`);
        }
      }

      if (event.type === "run-error" && event.message) {
        group.status = "FAILED";
        group.logs.push(`[run-error] ${event.message}`);
      }

      groups.set(stepKey, group);
    }

    const groupList = Array.from(groups.values()).sort((left, right) => {
      const leftStep = left.stepIndex ?? 0;
      const rightStep = right.stepIndex ?? 0;
      return leftStep - rightStep;
    });

    const updateCards = groupList
      .filter((group) => group.latestText)
      .sort(
        (left, right) =>
          right.messages.length - left.messages.length || (right.stepIndex ?? 0) - (left.stepIndex ?? 0),
      );

    return {
      conversations,
      groupList,
      updateCards,
    };
  }, [eventTrace]);

  useEffect(() => {
    if (!conversationRef.current) {
      return;
    }
    conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
  }, [timelineState.conversations.length]);

  return (
    <section className="panel timeline-panel">
      <div className="panel-header">
        <div>
          <p className="panel-eyebrow">{t("timeline.eyebrow")}</p>
          <h3>{t("timeline.title")}</h3>
          {currentRunId ? (
            <p className="panel-copy">
              {t("timeline.runId")}: <code>{currentRunId}</code>
              {currentWorkspacePath ? (
                <>
                  {" "}
                  {t("timeline.output")}: <code>{currentWorkspacePath}</code>
                </>
              ) : null}
            </p>
          ) : null}
        </div>
      </div>

      <div className="trace-panel">
        <div className="panel-header">
          <div>
            <p className="panel-eyebrow">Agent Conversation</p>
            <h3>Live Agent Messages</h3>
          </div>
        </div>
        <div className="conversation-feed" ref={conversationRef}>
          {timelineState.conversations.length === 0 ? (
            <p className="empty-text">{t("timeline.noEvents")}</p>
          ) : (
            timelineState.conversations.map((item) => (
              <article className="conversation-line" key={item.id}>
                <span className="conversation-line__agent">
                  {item.stepIndex ? `STEP ${item.stepIndex}` : "STEP"} | {item.agent}
                </span>
                <p>{item.text}</p>
              </article>
            ))
          )}
        </div>
      </div>

      {timelineState.updateCards.length > 0 ? (
        <div className="trace-panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Updates</p>
              <h3>Recently Updated Plans</h3>
            </div>
          </div>
          <div className="update-card-grid">
            {timelineState.updateCards.map((group) => (
              <article className="update-card" key={group.key}>
                <div className="timeline-item__top">
                  <strong>
                    STEP {group.stepIndex ?? "?"} | {group.agent}
                  </strong>
                  <StatusBadge
                    label={group.status}
                    tone={group.status === "COMPLETED" ? "success" : group.status === "FAILED" ? "danger" : "warning"}
                  />
                </div>
                <p className="panel-copy">{group.latestText}</p>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      {timelineState.groupList.length > 0 ? (
        <div className="trace-panel">
          <div className="panel-header">
            <div>
              <p className="panel-eyebrow">Step Details</p>
              <h3>Details</h3>
            </div>
          </div>
          <div className="detail-accordion">
            {timelineState.groupList.map((group) => (
              <details className="detail-card" key={group.key}>
                <summary>
                  <span>
                    STEP {group.stepIndex ?? "?"} | {group.agent}
                  </span>
                  <span>{group.messages.length} messages</span>
                </summary>
                {group.messages.length > 0 ? (
                  <div className="detail-card__section">
                    <strong>Agent messages</strong>
                    <div className="detail-card__body">
                      {group.messages.map((message, index) => (
                        <p key={`${group.key}-message-${index}`}>{message}</p>
                      ))}
                    </div>
                  </div>
                ) : null}
                <div className="detail-card__section">
                  <strong>Raw step log</strong>
                  <pre>{group.logs.join("\n\n") || t("timeline.noEvents")}</pre>
                </div>
                {group.summary ? (
                  <div className="detail-card__section">
                    <strong>Result summary</strong>
                    <p className="panel-copy">{group.summary}</p>
                  </div>
                ) : null}
              </details>
            ))}
          </div>
        </div>
      ) : null}

      {results.length === 0 ? (
        <p className="empty-text">{t("timeline.noOutput")}</p>
      ) : (
        <div className="timeline-list">
          {results.map((result, index) => (
            <article className="timeline-item" key={`${result.agent}-${index}`}>
              <div className="timeline-item__top">
                <strong>{result.agent}</strong>
                <StatusBadge
                  label={result.status}
                  tone={
                    result.status === "COMPLETED"
                      ? "success"
                      : result.status === "BLOCKED"
                        ? "danger"
                        : "warning"
                  }
                />
              </div>
              <p className="panel-copy">{result.summary}</p>
              {result.executor ? (
                <p className="panel-copy">
                  <strong>{t("timeline.executor")}:</strong> {result.executor}
                </p>
              ) : null}
              {result.generatedFiles.length > 0 ? (
                <ul className="mini-list">
                  {result.generatedFiles.slice(0, 6).map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function extractAgentMessage(message: string): string | null {
  const normalized = message.replace(/^\[stdout\]\s*/, "").trim();
  if (!normalized.startsWith("{")) {
    return null;
  }

  try {
    const parsed = JSON.parse(normalized) as {
      type?: string;
      item?: { type?: string; text?: string };
      text?: string;
    };

    if (parsed.item?.type === "agent_message" && typeof parsed.item.text === "string") {
      return parsed.item.text.trim();
    }

    if (parsed.type === "agent_message" && typeof parsed.text === "string") {
      return parsed.text.trim();
    }
  } catch {
    return null;
  }

  return null;
}
