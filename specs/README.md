# specs

모든 Specyn 실행은 Markdown spec bundle에서 시작한다.

## 필수 spec

- `product.md`
- `api.md`
- `test.md`
- `review.md`
- `agent.md`

## 공통 규칙

- YAML front matter 포함
- `목적`, `입력`, `출력`, `실행 규칙`, `Validation 기준`, `Prompt` 섹션 포함
- Prompt는 RIF(Role / Instructions / Format) 구조 권장
- `api.md`에는 구조 규칙(Spring Boot `global/common/domain`, FastAPI `app/global/common/domain`)을 넣는 편이 좋음
- `agent.md`에는 필요 시 `feedback_loops`와 `max_feedback_rounds`를 명시

## 빠른 시작

#### Linux / macOS
```bash
python3 specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service
python3 specyn.py validate --spec-dir specs/projects/sample-service
```

#### Windows (PowerShell)
```powershell
python specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service
python specyn.py validate --spec-dir specs/projects/sample-service
```
