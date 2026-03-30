ifeq ($(OS),Windows_NT)
SYSTEM_PYTHON ?= python
else
SYSTEM_PYTHON ?= python3
endif

TASK_RUNNER := scripts/specyn_tasks.py

.PHONY: help bootstrap doctor up dev ai-server backend frontend validate-spec init-spec compile-prompts run-sim run-example test-python build-frontend ci-local

help:
	@echo "Specyn 명령어"
	@echo "  make bootstrap       - Python/Frontend 의존성 설치 및 초기 폴더 준비"
	@echo "  make doctor          - 로컬 실행 환경 점검"
	@echo "  make up              - Docker Compose로 전체 스택 실행"
	@echo "  make dev             - 로컬 네이티브 모드로 전체 스택 실행"
	@echo "  make ai-server       - FastAPI만 실행"
	@echo "  make backend         - Spring Boot만 실행"
	@echo "  make frontend        - React UI만 실행"
	@echo "  make validate-spec   - 예제 spec bundle 검증"
	@echo "  make init-spec       - 새 spec bundle 템플릿 생성"
	@echo "  make compile-prompts - 예제 prompt 파일 생성"
	@echo "  make run-sim         - backend 없이 로컬 시뮬레이션 실행"
	@echo "  make run-example     - backend 경유 예제 실행"
	@echo "  make ci-local        - 로컬 CI 검증"

bootstrap:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) bootstrap

doctor:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) doctor

up:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) up

dev:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) dev

ai-server:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) ai-server

backend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) backend

frontend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) frontend

validate-spec:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) validate-spec

init-spec:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) init-spec

compile-prompts:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) compile-prompts

run-sim:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) run-sim

run-example:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) run-example

test-python:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) test-python

build-frontend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) build-frontend

ci-local:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) ci-local
