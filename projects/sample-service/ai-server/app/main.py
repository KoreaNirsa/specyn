from fastapi import FastAPI

app = FastAPI(title="sample-service-ai-server")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
