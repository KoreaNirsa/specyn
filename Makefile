ifeq ($(OS),Windows_NT)
SYSTEM_PYTHON ?= python
else
SYSTEM_PYTHON ?= python3
endif

TASK_RUNNER := scripts/specyn_tasks.py
SPECYN := $(SYSTEM_PYTHON) specyn.py

.PHONY: help setup auth-status doctor up down sample-up sample-down bootstrap dev ai-server backend frontend sample-dev sample-ai-server sample-backend sample-frontend validate-spec init-spec compile-prompts run-sim run-example sample-flow test-python build-frontend ci-local

help:
	@echo "Specyn 명령"
	@echo "  make setup            - .env 초기 설정과 인증 구성"
	@echo "  make auth-status      - 현재 인증과 .env 상태 확인"
	@echo "  make doctor           - 로컬 실행 환경 점검"
	@echo "  make up               - dashboard Docker Compose 실행"
	@echo "  make down             - dashboard Docker Compose 중지"
	@echo "  make sample-up        - sample-service Docker Compose 실행"
	@echo "  make sample-down      - sample-service Docker Compose 중지"
	@echo "  make bootstrap        - 호스트 기반 개발용 의존성 준비"
	@echo "  make dev              - 호스트 기반 dashboard 실행"
	@echo "  make ai-server        - 호스트 기반 dashboard ai-server 실행"
	@echo "  make backend          - 호스트 기반 dashboard backend 실행"
	@echo "  make frontend         - 호스트 기반 dashboard frontend 실행"
	@echo "  make sample-dev       - 호스트 기반 sample-service 실행"
	@echo "  make validate-spec    - sample-service spec bundle 검증"
	@echo "  make init-spec        - 새 spec bundle 템플릿 생성"
	@echo "  make compile-prompts  - sample-service prompt 파일 생성"
	@echo "  make run-sim          - backend 없이 로컬 시뮬레이션 실행"
	@echo "  make run-example      - dashboard backend 경유 실행"
	@echo "  make sample-flow      - sample-service validate -> compile-prompts -> run"
	@echo "  make ci-local         - 로컬 CI 검증"

setup:
	$(SPECYN) setup

auth-status:
	$(SPECYN) auth-status

doctor:
	$(SPECYN) doctor

up:
	$(SPECYN) up

down:
	$(SPECYN) down

sample-up:
	$(SPECYN) sample-up

sample-down:
	$(SPECYN) sample-down

bootstrap:
	$(SYSTEM_PYTHON) $(TASK_RUNNER) bootstrap

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
