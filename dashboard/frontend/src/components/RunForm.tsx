import { useForm } from "react-hook-form";

import { useRunSpecBundle } from "../hooks/useRunSpecBundle";
import { RunFormValues } from "../types";

const DEFAULT_VALUES: RunFormValues = {
  projectId: "sample-service",
  workspacePath: "projects/sample-service",
  ragEnabled: false,
};

/**
 * Run form for the current workflow.
 */
export function RunForm() {
  const mutation = useRunSpecBundle();
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<RunFormValues>({
    defaultValues: DEFAULT_VALUES,
  });

  const onSubmit = handleSubmit(async (values) => {
    await mutation.mutateAsync(values);
  });

  return (
    <section className="panel">
      <h2>Execution Settings</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Project ID
          <input {...register("projectId", { required: true })} readOnly />
        </label>
        <label>
          Workspace
          <input {...register("workspacePath", { required: true })} readOnly />
        </label>
        <label className="checkbox-row">
          <input type="checkbox" {...register("ragEnabled")} />
          Enable RAG agent
        </label>
        <button type="submit" disabled={isSubmitting || mutation.isPending}>
          {mutation.isPending ? "Running..." : "Run Agent"}
        </button>
      </form>
      {mutation.isError && (
        <div className="error-box">
          {(mutation.error as Error).message || "run request failed"}
        </div>
      )}
    </section>
  );
}
