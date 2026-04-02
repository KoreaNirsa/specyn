import { PageIntro } from "../components/PageIntro";
import { StatusBadge } from "../components/StatusBadge";
import { useI18n } from "../i18n";

/**
 * Handle agents page for the current workflow.
 */
export function AgentsPage() {
  const { t } = useI18n();

  const cards = [
    {
      title: t("agents.planner"),
      items: [t("agents.card1"), t("agents.card2"), t("agents.card3")],
    },
    {
      title: t("agents.backendFrontend"),
      items: [t("agents.card4"), t("agents.card5"), t("agents.card6")],
    },
    {
      title: t("agents.reviewDocs"),
      items: [t("agents.card7"), t("agents.card8"), t("agents.card9")],
    },
  ];

  return (
    <div className="page-grid page-grid--stacked">
      <PageIntro
        eyebrow={t("agents.eyebrow")}
        title={t("agents.title")}
        description={t("agents.description")}
        actions={<StatusBadge label={t("common.status.planned")} tone="warning" />}
      />
      <section className="triple-grid">
        {cards.map((card) => (
          <article className="panel placeholder-card" key={card.title}>
            <div className="placeholder-card__header">
              <h3>{card.title}</h3>
              <StatusBadge label={t("common.status.planned")} tone="warning" />
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
