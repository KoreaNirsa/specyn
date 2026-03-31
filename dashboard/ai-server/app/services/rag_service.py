from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
import sys

from app.core.config import get_settings
from app.models.contracts import RagSearchResponse


def should_use_langchain_runtime(version_info: tuple[int, int] | None = None) -> bool:
    version = version_info or sys.version_info[:2]
    return version < (3, 14)


@dataclass(frozen=True)
class _FallbackDocument:
    page_content: str
    metadata: dict[str, str]


class _FallbackRecursiveCharacterTextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: list[_FallbackDocument]) -> list[_FallbackDocument]:
        chunks: list[_FallbackDocument] = []
        for document in documents:
            text = document.page_content
            if len(text) <= self.chunk_size:
                chunks.append(document)
                continue

            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunks.append(
                    _FallbackDocument(
                        page_content=text[start:end],
                        metadata=document.metadata,
                    )
                )
                if end >= len(text):
                    break
                start = max(end - self.chunk_overlap, start + 1)
        return chunks


if should_use_langchain_runtime():
    try:
        from langchain_core.documents import Document
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ModuleNotFoundError:  # pragma: no cover - optional dependency fallback
        Document = _FallbackDocument  # type: ignore[assignment]
        RecursiveCharacterTextSplitter = _FallbackRecursiveCharacterTextSplitter  # type: ignore[assignment]
else:  # pragma: no cover - python 3.14+ compatibility fallback
    Document = _FallbackDocument  # type: ignore[assignment]
    RecursiveCharacterTextSplitter = _FallbackRecursiveCharacterTextSplitter  # type: ignore[assignment]


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9가-힣_\-]{2,}")


class RagService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_root = self.settings.project_root
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.rag_chunk_size,
            chunk_overlap=self.settings.rag_chunk_overlap,
        )

    async def search(self, query: str, top_k: int) -> RagSearchResponse:
        chunks = self._load_chunks()
        query_tokens = self._tokenize(query)

        scored: list[tuple[float, Document]] = []
        for chunk in chunks:
            score = self._score(query_tokens, chunk.page_content)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        items = [
            {
                "source": chunk.metadata.get("source", "unknown"),
                "score": round(score, 4),
                "content": chunk.page_content[:400],
            }
            for score, chunk in scored[:top_k]
        ]
        return RagSearchResponse(items=items)

    @lru_cache(maxsize=1)
    def _load_chunks(self) -> tuple[Document, ...]:
        documents: list[Document] = []
        for directory_name in ("docs", "agents", "specs"):
            base = self.project_root / directory_name
            if not base.exists():
                continue
            for path in sorted(base.rglob("*.md")):
                documents.append(
                    Document(
                        page_content=path.read_text(encoding="utf-8"),
                        metadata={"source": str(path.relative_to(self.project_root))},
                    )
                )

        if not documents:
            return tuple()

        return tuple(self.splitter.split_documents(documents))

    def _tokenize(self, text: str) -> set[str]:
        return {token.lower() for token in TOKEN_PATTERN.findall(text)}

    def _score(self, query_tokens: set[str], content: str) -> float:
        if not query_tokens:
            return 0.0
        content_lower = content.lower()
        hits = sum(1 for token in query_tokens if token in content_lower)
        return hits / len(query_tokens)
