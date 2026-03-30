import { HealthPanel } from "../components/HealthPanel";
import { ResultPanel } from "../components/ResultPanel";
import { RunForm } from "../components/RunForm";
import { SpecEditor } from "../components/SpecEditor";

export function WorkspacePage() {
  return (
    <div className="workspace-grid">
      <HealthPanel />
      <RunForm />
      <SpecEditor />
      <ResultPanel />
    </div>
  );
}
