interface Props {
  label: string;
  tone?: "default" | "success" | "warning" | "danger";
}

export function StatusBadge({ label, tone = "default" }: Props) {
  return <span className={`status-badge status-badge--${tone}`}>{label}</span>;
}
