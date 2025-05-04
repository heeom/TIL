## Servlet 이란?

- servlet은 HTTP 요청을 받아서 처리하고, HTTP 응답을 보내는 역할을 하는 서버 측 자바 클래스
    - javax.servlet.http.HttpServlet을 상속받아 작성한다.

### Servlet 동작 방식

1. 클라이언트에서 서버로 요청을 보냄 (URL)
2. Tomcat 같은 서블릿 컨테이너가 요청을 가로채서 URL에 매핑된 서블릿 클래스를 찾아서 실행
3. GET 요청 → doGet() 실행, POST 요청 → doPost() 메서드가 실행됨
4. 서블릿이 요청을 처리하고, HttpServletResponse으로 응답을 생성
5. 서블릿 컨테이너가 다시 클라이언트로 결과 전송

### Servlet 컨테이너?

- 서블릿 컨테이너는 서블릿을 실행하고, HTTP 요청, 응답을 처리해주는 서버 프로그램
    - Servlet은 자바 코드로 작성된 HTTP 처리 로직이고 (HttpServlet 을 상속받은 클래스)
    - Servlet Container가 로직을 호출, 초기화, 요청을 전달하고, 응답을 전송한다.
- 자바 서블릿만으로는 HTTP 요청을 받거나 응답을 내보낼 수 없고, Tomcat, Jetty 같은 서블릿 컨테이너가 있어야 한다.
- 클라이언트 HTTP 요청 수신, 응답 전송, 서블릿 매핑, 서블릿 생명 주기 관리, 스레드풀 관리 (병렬처리 가능하도록) → 모두 서블릿 컨테이너가 한다.

## Spring MVC의 Servlet

- 순수 서블릿은 HttpServletRequest, HttpServletResponse를 직접 다룸 → 요청 파라미터 파싱, 인코딩,  응답 포맷 생성을 직접 작성해야 해서 중복 코드가 발생하고, 비즈니스 로직과 서블릿 코드가 뒤섞여서 관심사 분리가 어려웠다.

### Spring Servlet의 핵심변화는 서블릿을 직접 쓰지 않게 해준것

- Spring MVC는 내부적으로는 여전히 서블릿을 사용하지만 서블릿을 직접 다루지 않도록 모든 것을 추상화해줌 → 개발자는 더 이상 HttpServlet을 직접 상속받아서 구현하지 않아도 된다.

### Spring MVC의 DispatcherServlet

- 스프링에서 자동등록되는 서블릿
- 모든 HTTP요청을 가로채서, 적절한 컨트롤러 메서드에 위임하고, 결과를 view 또는 JSON응답으로 만들어서 돌려준다.

### cf) Spring MVC 와 Spring WebFlux

| **Spring MVC** | **Spring WebFlux** |
| --- | --- |
| Servlet 기반 | Reactive Streams 기반 |
| 동기 | 비동기 |
| Blocking I/O | Non-blocking I/O |
| 스레드 수만큼 병렬 처리 가능 | 이벤트 루프 기반, 고부하 시스템에서 유리하다 |
| Tomcat, Jetty 서버 | Netty, Undertow 서버 |
| 요청 → 응답까지 한 스레드가 담당 | 요청 → DB I/O 중에는 스레드 반납 → 이벤트 콜백으로 결과 받아서 처리 |
- Spring MVC
    - 클라이언트 요청 → DispatcherServlet → HandlerMapping → Controller → ViewResolver → 응답
        - 요청마다 DispatcherServlet이 톰캣의 스레드 풀에서 서블릿에게 스레드를 하나씩 할당해서 처리한다.
- Spring WebFlux
    - 클라이언트 → WebHandler(DispatcherHandler) → RouterFunction → HandlerFunction → 응답 (Mono/Flux)
    

## Servlet 생명주기

- 서블릿은 톰캣 같은 서블릿 컨테이너가 관리하고, 스프링 빈은 스프링 컨테이너가 관리한다. 그렇다면 서로 다른 주체가 관리하는 이 두 객체는 어떻게 연결되어 동작하는걸까?

### Servlet 생명주기

- `init() → service() → destroy()`
- 서블릿 컨테이너가 서블릿 생성 → HTTP 요청을 위임 → 애플리케이션 종료시 차례대로 호출한다.

### ServletContext와 ApplicationContext의 연결
- ServletContext → DispatcherServlet → WebApplicationContext
1. Spring Boot 실행
    - Tomcat이 실행되면서 ServletContext가 생성된다 → Spring boot는 DispatcherServlet을 서블릿으로 등록한다
2. DispatcherServlet 초기화
    - DispatcherServlet은 초기화 과정에서 자신만의 WebApplicationContext를 생성 또는 주입받고, 내부에서 ServletContext를 사용해서 리소스에 접근하거나 등록한다.

- ServletContext
    - 웹 애플리케이션 전체에 대한 전역 정보를 담고 있음
    - 서블릿 컨테이너가 생성, 관리
    - 애플리케이션 당 하나만 존재하고, 모든 서블릿이 이 Context를 공유한다.

- ServletConfig
    - 서블릿 하나에 대한 설정 정보
    - 각 서블릿마다 개별적으로 존재한다

- WebApplicationContext
    - Spring 애플리케이션의 모든 Bean을 관리하는 컨테이너
    - Spring MVC에서는 DispatcherServlet이 WebApplicationContext를 생성하고, WebApplicationContext에서 내부적으로 ServletContext를 사용해서 설정정보를 가져온다.

### 그럼..Spring bean의 생명주기는 Servlet 컨테이너의 생명주기에 종속적인가?

- Spring Bean의 생명주기는 서블릿 컨테이너(Servlet Container)의 생명주기에 **간접적**으로 종속된다.
    - Spring Bean은 직접적으로는 DispatcherServlet이 생성한 WebApplicationContext가 관리한다.
    - WebApplicationContext는 ServletContext에 연결된다.
    - ServletContext가 destroy되면 WebApplicationContext도 destroy되고 이 때, Spring Bean도 소멸된다.
    - 즉, Spring Bean의 생명주기는 서블릿 컨테이너에 의해 간접적으로 제어된다.
