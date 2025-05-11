Java에서의 클래스 로딩 순서를 공부하다가, Spring Boot 애플리케이션에서도 같은 방식으로 클래스가 로딩되는지 궁금해져서 실제 로그를 통해 내부 클래스와 라이브러리들이 어떤 순서대로 로딩되는지 확인해봤다. 

### JAR 내부 구조

```bash
./gradlew bootJar 를 실행하면

build/lib/spring-boot-starter-0.0.1-SNAPSHOT.jar 경로에 실행가능한 jar파일이 생성된다.

jar -xf spring-boot-starter-0.0.1-SNAPSHOT.jar 으로 열어보면 아래 구조를 가진다
```

```bash
spring-boot-starter-0.0.1-SNAPSHOT.jar
├── META-INF/        ← 매니페스트, 서명 등 JAR 메타 정보
├── BOOT-INF/
│   ├── classes/     ← 애플리케이션 클래스
│   └── lib/         ← 의존성 라이브러리 JAR 모음
└── org/springframework/boot/loader/  ← Launcher 클래스
```

### 클래스 로딩 순서 (Spring Boot 3 기준)

1. JDK 기본 클래스 (jrt:/java.base)
    - java.lang.Object, java.lang.String, java.util.List 등
    - Bootstrap ClassLoader가 로드한다.
2. 애플리케이션 클래스 (BOOT-INF/classes/)
    - 개발자가 작성한 클래스
    - JarUrlClassLoader 등을 통해 BOOT-INF/classes/와 BOOT-INF/lib/*.jar 경로를 JDK의 기본 URLClassLoader 구조를 기반으로 로딩한다.
3. 외부라이브러리 클래스 : BOOT-INF/lib/*.jar
    - Gradle/Maven 의존성으로 포함된 외부 라이브러리 JAR들이 순차적으로 로딩된다.
    - SpringBoot의 LanchedClassLoader가 로드한다.
- cf) /webapp/WEB-INF/classes
    - War 파일 배포 방식에서만 사용된다.

### Spring boot 3 기준 예시

- `java -verbose:class -jar spring-boot-start-0.0.1-SNAPSHOT.jar`  으로 JAR 파일을 실행하면서 클래스 로딩 로그를 출력해봤다.

```bash
// 1. JDK 기본 클래스들을 먼저 로드한다.
[0.008s][info][class,load] java.lang.Object source: jrt:/java.base
[0.009s][info][class,load] java.io.Serializable source: jrt:/java.base
...

// 2. Spring Boot 런처 클래스 로딩 (org.springframework.boot.loader.launch.*)
// ExecutableArchiveLauncher, JarLauncher 등이 실행되며, 내부적으로 JarUrlClassLoader를 생성하여 BOOT-INF/classes/와 BOOT-INF/lib/*.jar 경로를 classpath에 등록한다.
nfo][class,load] org.springframework.boot.loader.launch.ExecutableArchiveLauncher source: file:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar
[0.046s][info][class,load] org.springframework.boot.loader.launch.JarLauncher source: file:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar
[0.046s][info][class,load] org.springframework.boot.loader.net.protocol.jar.JarUrlClassLoader source: file:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar
[0.046s][info][class,load] org.springframework.boot.loader.launch.LaunchedClassLoader source: file:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar
...

// 3. 애플리케이션 클래스 로딩 (BOOT-INF/classes)
// Spring Boot 런처가 LaunchedClassLoader에 의해 이 경로를 가장 우선순위로 설정함
[0.094s][info][class,load] com.example.springbootstart.SpringBootStartApplication source: jar:nested:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar/!BOOT-INF/classes/!/

// 4. 외부 라이브러리 클래스 로딩 (BOOT-INF/lib/*.jar)
// 애플리케이션 클래스 로딩 이후 외부 라이브러리가 로딩된다.
[0.109s][info][class,load] org.springframework.boot.SpringApplication source: jar:nested:/Users/spring-boot-start/build/libs/spring-boot-start-0.0.1-SNAPSHOT.jar/!BOOT-INF/lib/spring-boot-3.4.2.jar!/
```

- SpringBoot 런처 클래스
    - `ExecutableArchiveLauncher` , `JarLauncher`

> JarUrlClassLoader는 Spring Boot 3에서 도입된 전용 클래스 로더로, BOOT-INF/lib 내부의 JAR 파일을 중첩된 구조(nested jar) 상태로 분리 로딩할 수 있도록 설계되었다. 이는 기존의 LaunchedURLClassLoader를 대체하며, JarLauncher와 함께 동작한다.
>