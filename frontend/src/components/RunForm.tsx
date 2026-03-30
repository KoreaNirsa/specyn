import { useForm } from "react-hook-form";

import { useRunSpecBundle } from "../hooks/useRunSpecBundle";
import { RunFormValues } from "../types";

const DEFAULT_VALUES: RunFormValues = {
  projectId: "todo-service",
  workspacePath: ".workspace/todo-service",
  ragEnabled: false,
};

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
      <h2>실행 설정</h2>
      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Project ID
          <input {...register("projectId", { required: true })} />
        </label>
        <label>
          Workspace
          <input {...register("workspacePath", { required: true })} />
        </label>
        <label className="checkbox-row">
          <input type="checkbox" {...register("ragEnabled")} />
          RAG Agent 활성화
        </label>
        <button type="submit" disabled={isSubmitting || mutation.isPending}>
          {mutation.isPending ? "실행 중..." : "Agent 실행"}
        </button>
      </form>
      {mutation.isError && (
        <div className="error-box">
          {(mutation.error as Error).message || "실행 요청 중 오류가 발생했습니다."}
        </div>
      )}
    </section>
  );
}
