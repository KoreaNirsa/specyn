/**
 * Handle home page for the current workflow.
 */
export function HomePage() {
  return (
    <section className="page-grid">
      <article className="panel">
        <h2>Project Overview</h2>
        <p>
          Specyn connects a spec bundle, prompt generation, multi-agent execution, and output
          verification in one flow.
        </p>
        <p>
          The current reference output is <code>sample-service</code>. The dashboard now manages
          the agent run and writes artifacts into <code>projects/sample-service</code>.
        </p>
      </article>

      <article className="panel">
        <h2>Suggested Start</h2>
        <ol>
          <li><code>Copy-Item .env.example .env</code> or <code>cp .env.example .env</code></li>
          <li><code>python scripts/specyn_tasks.py bootstrap</code></li>
          <li><code>python scripts/specyn_tasks.py doctor</code></li>
          <li><code>python specyn.py setup</code></li>
          <li><code>python specyn.py up -d</code></li>
          <li><code>python specyn.py sample-up -d</code></li>
        </ol>
      </article>

      <article className="panel">
        <h2>What To Check</h2>
        <ul className="stack-list">
          <li>Open the dashboard workspace page and run the current spec bundle.</li>
          <li>Watch executor, step status, summaries, and stream trace in real time.</li>
          <li>Verify generated files are written under <code>projects/sample-service</code>.</li>
          <li>Use the sample-service frontend, backend, and AI server URLs for runtime checks.</li>
        </ul>
      </article>

      <article className="panel">
        <h2>Execution Mode</h2>
        <ul className="stack-list">
          <li>ChatGPT login uses Codex as the executor.</li>
          <li>OpenAI API authentication uses the OpenAI execution path.</li>
          <li>The dashboard remains the control plane in both cases.</li>
        </ul>
      </article>
    </section>
  );
}
