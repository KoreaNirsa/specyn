import { ReactNode } from "react";

import { StatusBadge } from "./StatusBadge";

interface Props {
  eyebrow: string;
  title: string;
  value: string;
  detail: string;
  badge?: { label: string; tone?: "default" | "success" | "warning" | "danger" };
  footer?: ReactNode;
}

/**
 * Handle metric card for the current workflow.
 */
export function MetricCard({ eyebrow, title, value, detail, badge, footer }: Props) {
  return (
    <article className="panel metric-card">
      <div className="metric-card__top">
        <div>
          <p className="panel-eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
        </div>
        {badge ? <StatusBadge label={badge.label} tone={badge.tone} /> : null}
      </div>
      <strong className="metric-card__value">{value}</strong>
      <p className="panel-copy">{detail}</p>
      {footer ? <div className="metric-card__footer">{footer}</div> : null}
    </article>
  );
}
