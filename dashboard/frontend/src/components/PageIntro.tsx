import { ReactNode } from "react";

interface Props {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}

/**
 * Handle page intro for the current workflow.
 */
export function PageIntro({ eyebrow, title, description, actions }: Props) {
  return (
    <section className="page-intro panel">
      <div>
        <p className="panel-eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-intro__description">{description}</p>
      </div>
      {actions ? <div className="page-intro__actions">{actions}</div> : null}
    </section>
  );
}
