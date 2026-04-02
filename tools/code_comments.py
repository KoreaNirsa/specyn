"""
여러 언어의 소스 파일에 함수/메서드 상단 주석을 자동으로 삽입하는 도우미 모듈이다.
파일 확장자별 주석 전략을 분기하고, 기존 주석 여부를 감지한 뒤 Python docstring이나 JSDoc/JavaDoc 스타일 블록을 생성해 삽입한다.
"""

from __future__ import annotations

import ast
from pathlib import Path
import re
from typing import Iterable


CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".sh"}
PYTHON_COMMENTABLE_NODES = (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef)
RESERVED_JS_METHOD_NAMES = {"if", "for", "while", "switch", "catch", "return"}
JAVA_SIGNATURE_PREFIXES = (
    "public",
    "protected",
    "private",
    "static",
    "final",
    "abstract",
    "default",
    "synchronized",
    "native",
)
RESERVED_JAVA_METHOD_NAMES = {"if", "for", "while", "switch", "catch", "return", "new", "throw", "try"}


def annotate_source(path: Path, content: str) -> str:
    """
    도구 계층에서 source에 설명용 주석을 추가한다.

    주요 흐름은 `annotate_python_source()`, `annotate_js_like_source()`, `annotate_java_source()`, `annotate_shell_source()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        path: 처리 대상 경로다.
        content: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    suffix = path.suffix.lower()
    if suffix == ".py":
        return annotate_python_source(content)
    if suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return annotate_js_like_source(content)
    if suffix == ".java":
        return annotate_java_source(content)
    if suffix == ".sh":
        return annotate_shell_source(content)
    return content


def should_annotate_path(path: Path) -> bool:
    """
    도구 계층에서 annotate 경로 여부를 판단한다.

    주요 흐름은 `lower()`, `any()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        path: 처리 대상 경로다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    ignored_parts = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "build", "dist", "out", "target"}
    return path.suffix.lower() in CODE_SUFFIXES and not any(part in ignored_parts for part in path.parts)


def annotate_python_source(content: str) -> str:
    """
    도구 계층에서 Python source에 설명용 주석을 추가한다.

    주요 흐름은 `parse()`, `splitlines()`, `walk()`, `get_docstring()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        content: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return content

    lines = content.splitlines()
    inserts: list[tuple[int, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, PYTHON_COMMENTABLE_NODES):
            continue
        if ast.get_docstring(node) is not None:
            continue
        if not getattr(node, "body", None):
            continue
        body_line = getattr(node.body[0], "lineno", node.lineno + 1)
        indent = _leading_whitespace(lines[body_line - 1]) if body_line - 1 < len(lines) else (_leading_whitespace(lines[node.lineno - 1]) + "    ")
        docstring_lines = _build_python_docstring_lines(node, indent)
        inserts.append((body_line - 1, docstring_lines))

    for index, docstring_lines in sorted(inserts, key=lambda item: item[0], reverse=True):
        lines[index:index] = docstring_lines
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def annotate_js_like_source(content: str) -> str:
    """
    도구 계층에서 js like source에 설명용 주석을 추가한다.

    주요 흐름은 `compile()`, `_annotate_line_based_source()`, `_match_js_signature()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        content: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    pattern_function = re.compile(r'^(\s*)(?:export\s+default\s+|export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(')
    pattern_arrow = re.compile(r'^(\s*)(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:<[^>]+>\s*)?\([^=]*\)\s*(?::[^=]+)?=>')
    pattern_method = re.compile(r'^(\s*)([A-Za-z_$][\w$]*)\s*\([^;]*\)\s*(?::[^=]+)?\s*\{\s*$')
    return _annotate_line_based_source(
        content,
        detectors=[
            lambda line: _match_js_signature(line, pattern_function, pattern_arrow, pattern_method),
        ],
        comment_builder=_build_js_comment_lines,
    )


def annotate_java_source(content: str) -> str:
    """
    도구 계층에서 java source에 설명용 주석을 추가한다.

    주요 흐름은 `compile()`, `_annotate_line_based_source()`, `_match_java_signature()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        content: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    class_pattern = re.compile(r'^(\s*)(?:public\s+|protected\s+|private\s+|abstract\s+|final\s+|sealed\s+|non-sealed\s+)*(class|record|interface|enum)\s+([A-Za-z_$][\w$]*)\b')
    constructor_pattern = re.compile(r'^(\s*)(?:public|protected|private)\s+([A-Za-z_$][\w$]*)\s*\([^;]*\)\s*(?:throws [^{]+)?\{\s*$')
    method_pattern = re.compile(r'^(\s*)(?:' + "|".join(JAVA_SIGNATURE_PREFIXES) + r')\s+[\w<>,\[\] ?.@]+\s+([A-Za-z_$][\w$]*)\s*\([^;]*\)\s*(?:throws [^{]+)?\{\s*$')
    return _annotate_line_based_source(
        content,
        detectors=[
            lambda line: _match_java_signature(line, class_pattern, constructor_pattern, method_pattern),
        ],
        comment_builder=_build_java_comment_lines,
        annotation_prefix='@',
    )


def annotate_shell_source(content: str) -> str:
    """
    도구 계층에서 셸 source에 설명용 주석을 추가한다.

    주요 흐름은 `compile()`, `_annotate_line_based_source()`, `_match_shell_signature()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        content: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    pattern = re.compile(r'^(\s*)(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{\s*$')
    return _annotate_line_based_source(
        content,
        detectors=[lambda line: _match_shell_signature(line, pattern)],
        comment_builder=_build_shell_comment_lines,
    )


def annotate_paths(paths: Iterable[Path]) -> list[Path]:
    """
    도구 계층에서 경로 목록에 설명용 주석을 추가한다.

    주요 흐름은 `annotate_source()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        paths: 처리 대상 경로 목록이다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    changed_paths: list[Path] = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        annotated = annotate_source(path, original)
        if annotated == original:
            continue
        path.write_text(annotated, encoding="utf-8")
        changed_paths.append(path)
    return changed_paths


def _annotate_line_based_source(
    content: str,
    *,
    detectors: list,
    comment_builder,
    annotation_prefix: str | None = None,
) -> str:
    """
    모듈 내부 전용 헬퍼로, line based source에 설명용 주석을 추가한다.

    주요 흐름은 `splitlines()`, `detector()`, `_has_existing_comment()`, `comment_builder()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        content: 문자열 입력값이다.
        detectors: 순서를 유지하는 목록 입력값이다.
        comment_builder: 주석 builder과(와) 관련된 입력값이다.
        annotation_prefix: annotation prefix을(를) 나타내는 `str | None` 타입 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    lines = content.splitlines()
    inserts: list[tuple[int, list[str]]] = []
    for index, line in enumerate(lines):
        match = None
        for detector in detectors:
            match = detector(line)
            if match is not None:
                break
        if match is None:
            continue
        indent, name, kind = match
        insert_at = index
        if annotation_prefix is not None:
            while insert_at > 0 and lines[insert_at - 1].strip().startswith(annotation_prefix):
                insert_at -= 1
        if _has_existing_comment(lines, insert_at):
            continue
        inserts.append((insert_at, comment_builder(indent, name, kind)))
    for index, comment_lines in sorted(inserts, key=lambda item: item[0], reverse=True):
        lines[index:index] = comment_lines
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def _match_js_signature(line: str, function_pattern: re.Pattern[str], arrow_pattern: re.Pattern[str], method_pattern: re.Pattern[str]) -> tuple[str, str, str] | None:
    """
    모듈 내부 전용 헬퍼로, `match_js_signature()`가 맡는 js signature 관련 작업을 수행한다.

    주요 흐름은 `match()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        line: 문자열 입력값이다.
        function_pattern: function pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.
        arrow_pattern: arrow pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.
        method_pattern: method pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.

    Returns:
        함수에서 조립한 `tuple[str, str, str] | None` 타입 결과다.
    """
    for pattern, kind in ((function_pattern, "function"), (arrow_pattern, "function"), (method_pattern, "method")):
        match = pattern.match(line)
        if match is None:
            continue
        indent, name = match.group(1), match.group(2)
        if name in RESERVED_JS_METHOD_NAMES:
            return None
        return indent, name, kind
    return None


def _match_java_signature(line: str, class_pattern: re.Pattern[str], constructor_pattern: re.Pattern[str], method_pattern: re.Pattern[str]) -> tuple[str, str, str] | None:
    """
    모듈 내부 전용 헬퍼로, `match_java_signature()`가 맡는 java signature 관련 작업을 수행한다.

    주요 흐름은 `match()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        line: 문자열 입력값이다.
        class_pattern: class pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.
        constructor_pattern: constructor pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.
        method_pattern: method pattern을(를) 나타내는 `re.Pattern[str]` 타입 입력값이다.

    Returns:
        함수에서 조립한 `tuple[str, str, str] | None` 타입 결과다.
    """
    class_match = class_pattern.match(line)
    if class_match is not None:
        return class_match.group(1), class_match.group(3), "class"
    if "(" not in line or ")" not in line:
        return None
    constructor_match = constructor_pattern.match(line)
    if constructor_match is not None:
        constructor_name = constructor_match.group(2)
        if constructor_name in RESERVED_JAVA_METHOD_NAMES:
            return None
        return constructor_match.group(1), constructor_name, "method"
    method_match = method_pattern.match(line)
    if method_match is None:
        return None
    method_name = method_match.group(2)
    if method_name in RESERVED_JAVA_METHOD_NAMES:
        return None
    return method_match.group(1), method_name, "method"


def _match_shell_signature(line: str, pattern: re.Pattern[str]) -> tuple[str, str, str] | None:
    """
    모듈 내부 전용 헬퍼로, `match_shell_signature()`가 맡는 셸 signature 관련 작업을 수행한다.

    주요 흐름은 `match()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        line: 문자열 입력값이다.
        pattern: 문자열 검색에 사용할 정규식 패턴이다.

    Returns:
        함수에서 조립한 `tuple[str, str, str] | None` 타입 결과다.
    """
    match = pattern.match(line)
    if match is None:
        return None
    return match.group(1), match.group(2), "function"


def _has_existing_comment(lines: list[str], insert_at: int) -> bool:
    """
    모듈 내부 전용 헬퍼로, existing 주석 여부를 판단한다.

    주요 흐름은 `strip()`, `startswith()`, `endswith()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        lines: 순서를 유지하는 목록 입력값이다.
        insert_at: 정수 입력값이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    previous_index = insert_at - 1
    while previous_index >= 0 and not lines[previous_index].strip():
        previous_index -= 1
    if previous_index < 0:
        return False
    stripped = lines[previous_index].strip()
    return stripped.startswith("/**") or stripped.startswith("//") or stripped.startswith("#") or stripped.endswith("*/") or stripped.startswith('"""') or stripped.startswith("'''")


def _build_python_docstring_lines(node: ast.AST, indent: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, Python docstring lines을(를) 조립하거나 생성한다.

    주요 흐름은 `_sentence_for_identifier()`, `arguments()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        node: node을(를) 나타내는 `ast.AST` 타입 입력값이다.
        indent: 문자열 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    summary = _sentence_for_identifier(getattr(node, "name", "object"), kind="class" if isinstance(node, ast.ClassDef) else "function")
    parameter_names = [
        argument.arg
        for argument in getattr(node, "args", ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])).args
        if argument.arg not in {"self", "cls"}
    ]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.args.vararg is not None:
        parameter_names.append(node.args.vararg.arg)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.args.kwarg is not None:
        parameter_names.append(node.args.kwarg.arg)
    if not parameter_names:
        return [f'{indent}"""{summary}"""']

    lines = [f'{indent}"""{summary}', "", f"{indent}Args:"]
    for name in parameter_names:
        lines.append(f"{indent}    {name}: Input parameter consumed by this routine.")
    lines.append(f'{indent}"""')
    return lines


def _build_js_comment_lines(indent: str, name: str, kind: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, js 주석 lines을(를) 조립하거나 생성한다.

    주요 흐름은 `_sentence_for_identifier()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        indent: 문자열 입력값이다.
        name: 문자열 입력값이다.
        kind: 문자열 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    summary = _sentence_for_identifier(name, kind=kind)
    return [f"{indent}/**", f"{indent} * {summary}", f"{indent} */"]


def _build_java_comment_lines(indent: str, name: str, kind: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, java 주석 lines을(를) 조립하거나 생성한다.

    주요 흐름은 `_sentence_for_identifier()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        indent: 문자열 입력값이다.
        name: 문자열 입력값이다.
        kind: 문자열 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    summary = _sentence_for_identifier(name, kind=kind)
    return [f"{indent}/**", f"{indent} * {summary}", f"{indent} */"]


def _build_shell_comment_lines(indent: str, name: str, _: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, 셸 주석 lines을(를) 조립하거나 생성한다.

    주요 흐름은 `_sentence_for_identifier()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        indent: 문자열 입력값이다.
        name: 문자열 입력값이다.
        _: 문자열 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    summary = _sentence_for_identifier(name, kind="function")
    return [f"{indent}# {summary}"]


def _sentence_for_identifier(identifier: str, *, kind: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `sentence_for_identifier()`가 맡는 for 식별자 관련 작업을 수행한다.

    주요 흐름은 `_split_identifier()`, `capitalize()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        identifier: 문자열 입력값이다.
        kind: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    words = _split_identifier(identifier)
    if not words:
        return "Describe the current routine."
    first, rest = words[0], words[1:]
    remainder = " ".join(rest) if rest else "routine"
    verb_map = {
        "build": f"Build {remainder} for the current module.",
        "create": f"Create {remainder} for the current module.",
        "collect": f"Collect {remainder} used by the current workflow.",
        "compile": f"Compile {remainder} for the current workflow.",
        "delete": f"Delete {remainder} for the current workflow.",
        "ensure": f"Ensure {remainder} is ready for the current workflow.",
        "execute": f"Execute {remainder} for the current workflow.",
        "generate": f"Generate {remainder} for the current workflow.",
        "get": f"Return {remainder} for the current workflow.",
        "handle": f"Handle {remainder} for the current workflow.",
        "include": f"Include {remainder} in the current workflow.",
        "init": f"Initialize {remainder} for the current workflow.",
        "iter": f"Iterate over {remainder} for the current workflow.",
        "load": f"Load {remainder} for the current workflow.",
        "main": "Run the main entry point for the current module.",
        "match": f"Match {remainder} for the current workflow.",
        "normalize": f"Normalize {remainder} for the current workflow.",
        "parse": f"Parse {remainder} for the current workflow.",
        "prepare": f"Prepare {remainder} for the current workflow.",
        "print": f"Print {remainder} for the current workflow.",
        "read": f"Read {remainder} for the current workflow.",
        "refresh": f"Refresh {remainder} for the current workflow.",
        "resolve": f"Resolve {remainder} for the current workflow.",
        "run": f"Run {remainder} for the current workflow.",
        "search": f"Search {remainder} for the current workflow.",
        "should": f"Determine whether {remainder} should be used in the current workflow.",
        "start": f"Start {remainder} for the current workflow.",
        "terminate": f"Terminate {remainder} for the current workflow.",
        "update": f"Update {remainder} for the current workflow.",
        "validate": f"Validate {remainder} for the current workflow.",
        "wait": f"Wait for {remainder} in the current workflow.",
        "write": f"Write {remainder} for the current workflow.",
    }
    if kind == "class":
        return f"Provide {" ".join(words)} behavior for the current module.".capitalize()
    if kind == "method" and first == "get":
        return f"Return {remainder} for the current object.".capitalize()
    return verb_map.get(first, f"Handle {' '.join(words)} for the current workflow.").capitalize()


def _split_identifier(identifier: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, `split_identifier()`가 맡는 식별자 관련 작업을 수행한다.

    주요 흐름은 `sub()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        identifier: 문자열 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    normalized = identifier.replace("-", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", normalized)
    return [token.lower() for token in normalized.split("_") if token]


def _leading_whitespace(line: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `leading_whitespace()`가 맡는 whitespace 관련 작업을 수행한다.

    주요 흐름은 `len()`, `lstrip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        line: 문자열 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return line[: len(line) - len(line.lstrip())]
