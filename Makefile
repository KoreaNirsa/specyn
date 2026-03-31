ifeq ($(OS),Windows_NT)
SYSTEM_PYTHON ?= python
else
SYSTEM_PYTHON ?= python3
endif

TASK_RUNNER := scripts/specyn_tasks.py

.PHONY: help bootstrap doctor up dev ai-server backend frontend sample-dev sample-ai-server sample-backend sample-frontend validate-spec init-spec compile-prompts run-sim run-example sample-flow test-python build-frontend ci-local

help:
	@echo "Specyn 명령어"
	@echo "  make bootstrap        - 의존성 설치 및 로컬 폴더 준비"
	@echo "  make doctor           - 로컬 실행 환경 점검"
	@echo "  make up               - dashboard Docker Compose 실행"
	@echo "  make dev              - dashboard(frontend/backend/ai-server) 실행"
	@echo "  make ai-server        - dashboard AI Server 실행"
	@echo "  make backend          - dashboard Backend 실행"
	@echo "  make frontend         - dashboard Frontend 실행"
	@echo "  make sample-dev       - sample-service 실제 프로젝트 런타임 실행"
	@echo "  make sample-ai-server - sample-service AI Server 실행"
	@echo "  make sample-backend   - sample-service Backend 실행"
	@echo "  make sample-frontend  - sample-service Frontend 실행"
	@echo "  make validate-spec    - sample-service spec bundle 검증"
	@echo "  make init-spec        - 새 spec bundle 템플릿 생성"
	@echo "  make compile-prompts  - sample-service prompt 파일 생성"
	@echo "  make run-sim          - backend 없이 로컬 시뮬레이션 실행"
	@echo "  make run-example      - dashboard backend 경유 예제 실행"
	@echo "  make sample-flow      - sample-service validate -> compile-prompts -> run"
	@echo "  make ci-local         - 로컬 CI 검증"

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

sample-dev:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) sample-dev

sample-ai-server:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) sample-ai-server

sample-backend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) sample-backend

sample-frontend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) sample-frontend

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

sample-flow:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) sample-flow

test-python:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) test-python

build-frontend:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) build-frontend

ci-local:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) ci-local
