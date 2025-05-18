health 체크를 할 때만 사용해봤는데, 다른 기능은 어떤게 있는지 궁금해서 찾아보게 되었다.

- Spring boot 애플리케이션을 운영하는데 도움을 주는 정보들을 제공해주는 모듈이다. spring boot의 모니터링 기능이라고 보면 된다.
- Spring boot 애플리케이션의 각종 정보를 엔드포인트를 통해 확인할 수 있는데,
    - JMX 또는 HTTP를 통해 접근 가능하다.
    - shutdown을 제외한 모든 Endpoint는 기본적으로 활성화 상태다.
    - actuator를 통해 heapdump, threaddump 를 뜰 수도 있고, logfile도 볼 수 있다.
- HTTP 사용해서 접근
    - `/actuator`
    - health, info를 제외한 대부분의 Endpoint는 기본적으로 비공개 상태

- build.gradle 에 간단하게 web과 actuator 의존성만 추가해서 직접 어떤 기능이 있는지 확인해보자.

```groovy
implementation 'org.springframework.boot:spring-boot-starter-web'
implementation 'org.springframework.boot:spring-boot-starter-actuator'
```

- MainApi

```java
@RestController
@RequestMapping("/api")
public class MainApi {

    @GetMapping("/log")
    public String log() {
        return "Hello World";
    }
}
```

- 애플리케이션을 실행하고 /actuator에 접근해보면 기본적으로 아래 endpoint만 공개되어 있다. HTTP를 사용하면 기본적으로 /health, /info 정도의 endpoint만 공개되어 있다. 나머지 enpoint 들은 필요하다면 application.yml 설정을 통해 노출할 수 있다.
    - `GET /actuator`는 사용가능한 endpoint 목록을 보여준다.

```json
GET http://127.0.0.1:8080/actuator

{
  "_links": {
    "self": {
      "href": "http://127.0.0.1:8080/actuator",
      "templated": false
    },
    "health": {
      "href": "http://127.0.0.1:8080/actuator/health",
      "templated": false
    },
    "health-path": {
      "href": "http://127.0.0.1:8080/actuator/health/{*path}",
      "templated": true
    }
  }
}
```

이제 자주 사용되는 주요 endpoint들을 알아보자.

```yaml
# 직접 endpoint를 확인해보기 위해 application.yml 에 모든 endpoint를 공개하도록 설정했다.
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

### /actuator/health

- 애플리케이션의 상태를 반환한다.

```json
GET http://127.0.0.1:8080/actuator/health

{
  "status": "UP"
}
```

### /actuator/info

- 프로젝트 버전 등 애플리케이션의 메타데이터를 확인할 수 있다.

```json
GET http://127.0.0.1:8080/actuator/info

{
  "build": {
    "artifact": "spring-actuator",
    "name": "spring-actuator",
    "time": "2025-05-18T13:51:12.821Z",
    "version": "0.0.1-SNAPSHOT",
    "group": "com.example"
  }
}
```

### **/actuator/metrics**

- 애플리케이션의 성능 및 상태 관련 측정 지표를 확인할 수 있다.
    - 메모리, GC, 트래픽 등…
    - 측정값을 보려면 /actuator/metrics/{[metric.name](http://metric.name/)} 형식으로 요청해야 한다.

```graphql
# 1. 메모리 사용량
GET http://127.0.0.1:8080/actuator/metrics/jvm.memory.used # 실제 사용중인 메모리
GET http://127.0.0.1:8080/actuator/metrics/jvm.memory.max # 최대 메모리

# 2. GC
GET http://127.0.0.1:8080/actuator/metrics/jvm.gc.memory.allocated # 할당된 메모리 총량
GET http://127.0.0.1:8080/actuator/metrics/jvm.gc.pause #GC로 인한 일시중지 시간

# 3. HTTP 트래픽
GET http://127.0.0.1:8080/actuator/metrics/http.server.requests
```

- availableTags에서 어떤 태그로 필터링 가능한지 확인해보고 특정 요청, method등으로 조건을 걸면 범위를 좁힐 수 있다.

```graphql
# 특정 URI 에 대한 요청 시간 측정값
GET http://localhost:8080/actuator/metrics/http.server.requests?tag=uri:/api/log
```

### **/actuator/env**

- 현재 애플리케이션의 환경 변수 및 설정 값

### **/actuator/beans**

- 현재 컨테이너에 등록된 모든 Spring Bean 목록

### /actuator/threaddump

- 현재 애플리케이션의 스레드 덤프를 출력

https://docs.spring.io/spring-boot/reference/actuator/endpoints.html

공식문서에서 더 많은 endpoint들을 찾을 수 있다. 중요한건 spring actuator 가 제공하는 기능 자체보단 spring actuator가 제공하는 메트릭을 외부 툴과 연동해서

모니터링 및 성능 이슈를 조기 감지 할 수 있도록 잘 조합해서 쓰는 거 같다.