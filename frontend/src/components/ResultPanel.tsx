import { useWorkspaceStore } from "../store/workspaceStore";

export function ResultPanel() {
  const results = useWorkspaceStore((state) => state.results);

  return (
    <section className="panel">
      <h2>실행 결과</h2>
      {results.length === 0 ? (
        <p>아직 실행 결과가 없습니다.</p>
      ) : (
        <div className="results-grid">
          {results.map((result) => (
            <article className="result-card" key={`${result.agent}-${result.summary}`}>
              <h3>{result.agent}</h3>
              <p><strong>Status:</strong> {result.status}</p>
              <pre>{result.summary}</pre>
              {result.generatedFiles.length > 0 && (
                <>
                  <strong>Generated Files</strong>
                  <ul>
                    {result.generatedFiles.map((file) => (
                      <li key={file}>{file}</li>
                    ))}
                  </ul>
                </>
              )}
              <strong>Validations</strong>
              <ul>
                {result.validations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
