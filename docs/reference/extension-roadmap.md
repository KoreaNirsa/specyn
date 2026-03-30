# Extension Roadmap

이 문서는 장기 확장 방향을 빠르게 훑어보기 위한 요약본입니다.

## 플랫폼 확장

- Backend: ECS/Fargate 또는 EKS
- AI Server: 별도 private service
- Workspace / Artifacts: S3 또는 object storage
- Queue: SQS, Kafka, RabbitMQ
- Secret: Secrets Manager / Vault / 사내 secret manager

## 온프레미스 확장

- Backend / AI Server를 내부 VM 또는 K8s에 분리 배포
- 사내 Git 서버 / artifact 저장소 / secret manager 연동
- 폐쇄망용 모델 프록시 또는 사내 LLM 게이트웨이 연계

## 운영 품질 확장

- policy pack
- review pack / security pack
- telemetry / metrics / tracing
- 비용/토큰 사용량 집계
