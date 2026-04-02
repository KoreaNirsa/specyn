# 07. Extension Roadmap

이 저장소는 CI 범위까지만 기본 제공하지만, 다음 확장을 고려해 구조를 설계했다.

## 1. 플랫폼 확장

- Backend: ECS/Fargate 또는 EKS
- AI Server: 별도 private service
- Workspace/artifacts: S3 또는 object storage
- Queue: SQS, Kafka, RabbitMQ
- Secret: Secrets Manager / Vault / 사내 secret manager

## 2. 온프레미스 확장

- Backend / AI Server를 내부 VM 또는 K8s에 분리 배포
- 사내 Git 서버 / artifact 저장소 / secret manager 연동
- 폐쇄망용 모델 프록시 또는 사내 LLM 게이트웨이 연계

## 3. Kubernetes 확장

- backend / ai-server / frontend를 개별 deployment로 분리
- workspace는 PVC 또는 object storage + runner 패턴으로 전환
- job 기반 Codex/worker 실행기로 분리 가능

## 4. 개발 생산성 확장

- branch-per-run
- PR bot / GitHub App 연동
- spec drift 탐지 자동화
- reusable workflow / self-hosted runner

## 5. 사용자 편의성 확장

향후 다음 기능을 자연스럽게 붙일 수 있도록 구조를 열어 두었다.

- Agent 실행 대시보드
- step-by-step timeline
- agent trace / audit view
- prompt snapshot browser
- run history / artifact catalog
- 실패 원인 분석 보드

## 6. 운영 품질 확장

- 정책 팩(policy pack)
- 팀별 review pack / security pack
- 텔레메트리 / metrics / tracing
- 비용/토큰 사용량 집계
