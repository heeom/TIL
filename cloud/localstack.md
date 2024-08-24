### LocalStack?

- 클라우드 application 개발을 위한 테스트/모킹 프레임워크
- AWS 환경에서 제공하는 기능을 로컬에서 사용할 수 있다.

AWS Simple Queue Service를 로컬 환경에서 사용하기 위해 LocalStack 설치

### docker-compose.yml 파일 생성

```yaml

version: "3.8"
services:
  localstack:
    container_name: "localstack"
    image: localstack/localstack:2.2.0 # latest를 사용하면 예상못한 버전업으로 인해 오류가 발생할 수 있기 때문에 버전 고정해서 사용
    restart: always
    ports:
      - "127.0.0.1:4566:4566"            # LocalStack Gateway
      - "127.0.0.1:4510-4559:4510-4559"  # external services port range
    environment:
      - DEBUG=${DEBUG-}
      - DOCKER_HOST=unix:///var/run/docker.sock
      - AWS_ACCESS_KEY_ID=test # 임의 지정
      - AWS_SECRET_ACCESS_KEY=1234
      - AWS_DEFAULT_REGION=us-east-1
    ports:
      - '4566:4566'

```

- localStack 컨테이너 실행

```bash
docker compose up -d
```

### Sqs 생성

- localStack 컨테이너로 접속

```bash
localstack docker exec -it localstack sh
```

- 사용할 sqs를 생성한다.

```bash
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name test-queue.fifo --attributes FifoQueue=true
```