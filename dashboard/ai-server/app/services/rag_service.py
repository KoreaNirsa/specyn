"""
문서 디렉터리를 청크 단위로 읽어 간단한 토큰 기반 유사도로 검색하는 RAG 서비스 모듈이다.
LangChain이 설치된 경우와 설치되지 않은 경우를 모두 지원하며, 검색 결과를 동일한 응답 모델로 반환해 상위 서비스가 구현 차이를 숨길 수 있게 한다.
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
import sys

from app.core.config import get_settings
from app.models.contracts import RagSearchResponse


def should_use_langchain_runtime(version_info: tuple[int, int] | None = None) -> bool:
    """
    AI Server 서비스 계층에서 use LangChain 런타임 여부를 판단한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Args:
        version_info: 파이썬 버전 비교에 사용할 버전 튜플이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    version = version_info or sys.version_info[:2]
    return version < (3, 14)


@dataclass(frozen=True)
class _FallbackDocument:
    """
    문서 본문과 메타데이터를 함께 보관해 후속 단계가 재해석 없이 재사용할 수 있게 하는 모델이다.

    Attributes:
        page_content: 인스턴스가 내부적으로 유지하는 페이지 content 관련 상태다.
        metadata: YAML front matter나 설정에서 읽어 온 메타데이터 딕셔너리다.
    """
    page_content: str
    metadata: dict[str, str]


class _FallbackRecursiveCharacterTextSplitter:
    """
    선택적 의존성이 없을 때 기본 동작을 대체하기 위한 fallback 구현이다.

    외부에서 주로 읽어야 할 메서드는 `split_documents()`이다.

    Attributes:
        chunk_size: 인스턴스가 내부적으로 유지하는 청크 size 관련 상태다.
        chunk_overlap: 인스턴스가 내부적으로 유지하는 청크 overlap 관련 상태다.
    """
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """
        `_FallbackRecursiveCharacterTextSplitter` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

        Args:
            chunk_size: 정수 입력값이다.
            chunk_overlap: 정수 입력값이다.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: list[_FallbackDocument]) -> list[_FallbackDocument]:
        """
        `_FallbackRecursiveCharacterTextSplitter`의 공개 메서드로, `split_documents()`가 맡는 문서 목록 관련 작업을 수행한다.

        주요 흐름은 `_FallbackDocument()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            documents: 요청에 포함된 spec 문서 목록이다.

        Returns:
            조건에 맞춰 수집하거나 정렬한 목록이다.
        """
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
    """
    AI Server 서비스 계층에서 핵심 비즈니스 흐름을 조율하는 서비스 클래스다.

    외부에서 주로 읽어야 할 메서드는 `search()`이다.

    Attributes:
        settings: 런타임 동작을 제어하는 설정 객체다.
        project_root: 프로젝트 루트 경로다.
        splitter: 인스턴스가 내부적으로 유지하는 splitter 관련 상태다.
    """
    def __init__(self) -> None:
        """
        `RagService` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        주요 흐름은 `get_settings()`, `RecursiveCharacterTextSplitter()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        """
        self.settings = get_settings()
        self.project_root = self.settings.project_root
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.rag_chunk_size,
            chunk_overlap=self.settings.rag_chunk_overlap,
        )

    async def search(self, query: str, top_k: int) -> RagSearchResponse:
        """
        `RagService`의 공개 메서드로, `search()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `_load_chunks()`, `_tokenize()`, `_score()`, `sort()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            query: RAG 검색이나 조회에 사용할 질의 문자열이다.
            top_k: 반환할 상위 검색 결과 개수다.

        Returns:
            함수에서 조립한 `RagSearchResponse` 타입 결과다.
        """
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
        """
        `RagService` 내부에서만 사용하는 보조 메서드로, 청크 목록을(를) 외부 소스에서 읽어 들인다.

        주요 흐름은 `lru_cache()`, `rglob()`, `Document()`, `split_documents()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Returns:
            함수에서 조립한 `tuple[Document, ...]` 타입 결과다.
        """
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
        """
        `RagService` 내부에서만 사용하는 보조 메서드로, `tokenize()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `findall()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

        Returns:
            함수에서 조립한 `set[str]` 타입 결과다.
        """
        return {token.lower() for token in TOKEN_PATTERN.findall(text)}

    def _score(self, query_tokens: set[str], content: str) -> float:
        """
        `RagService` 내부에서만 사용하는 보조 메서드로, `score()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `sum()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            query_tokens: query tokens을(를) 나타내는 `set[str]` 타입 입력값이다.
            content: 문자열 입력값이다.

        Returns:
            함수에서 조립한 `float` 타입 결과다.
        """
        if not query_tokens:
            return 0.0
        content_lower = content.lower()
        hits = sum(1 for token in query_tokens if token in content_lower)
        return hits / len(query_tokens)
