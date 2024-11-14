# Lombok @RequiredArgsConstructor으로 생성된 생성자와 @Qualifier를 함께 사용할 때 발생하는 문제

## 문제 발생 상황

- Lombok의 @RequiredArgsConstructor와 함께 주입할 필드를 private final로 선언하여 생성자 주입 방식으로 객체를 생성하고 있었음
- 동일한 타입의 bean이 여러개일 때, 특정 bean을 주입하기 위해 `@Qulifier` 를 사용하려고 했다.
- 그러나,  `@Qualifier` 로 명시한 bean이 아닌 `@Primary` 로 선언된 빈이 주입되는 문제가 발생했다.
- 문제 발생 코드

```java
@Configuration
public class SpringConfig {

    @Primary
    @Bean
    public MyComponent primaryComponent() {
        return new PrimaryComponent();
    }

    @Bean // Myservice에서 주입 받을 bean
    public MyComponent secondaryComponent() {
        return new SecondaryComponent();
    }
}
```

```java
@Slf4j
@Component
@RequiredArgsConstructor
public class MyService {

    @Qualifier("secondaryComponent")
    private final MyComponent secondaryComponent;

    @PostConstruct
    public void initiate() {
        log.info("MyService initiate. MyComponent {}", secondaryComponent.getClass().getName());
    }

}
```

```bash
2024-11-14T21:17:44.735+09:00  INFO 74389 --- [spring-web] [           main] o.example.springweb.service.MyService    : MyService initiate. MyComponent org.example.springweb.service.bean_injection.PrimaryComponent
```

## Lombok의 생성자 생성 방식

- Lombok의 @RequiredArgsConstructor는 필드 이름만을 기준으로 생성자를 자동 생성하기 때문에, 필드에 적용된 @Qualifier 애너테이션이 생성자 파라미터에 포함되지 않음.
- 즉, Lombok은 @Qualifier 애너테이션을 생성자 파라미터에 복사하지 않기 때문에 의도했던 빈이 주입되지 않음.
- 예상했던 생성자 형태는 다음과 같지만

```java
public MyService(@Qualifier("secondaryComponent") MyComponent secondaryComponent) {
        this.secondaryComponent = secondaryComponent;
    }
```

- @RequiredArgsConstructor가 실제로 생성하는 생성자는 @Qualifier 애너테이션을  포함하지 않는다.

```java
@Generated
    public MyService(final MyComponent secondaryComponent) {
        this.secondaryComponent = secondaryComponent;
    }
```

- 따라서, 의도한 특정 빈이 아닌 @Primary로 지정된 빈이 주입된다.

## 해결방법

- 따라서 @Qualifier를 통해 의도한 빈을 주입하려면 직접 생성자를 작성하거나 필드 주입방식을 사용하자.
- 직접 생성자를 작성

```java
@Component
public class MyService {
    private final MyComponent secondaryComponent;
    
    public MyService(@Qualifier("secondaryComponent") MyComponent secondaryComponent) {
        this.secondaryComponent = secondaryComponent;
    }
}
```

- 필드 주입방식 사용

```java
@Autowired
@Qualifier("secondaryComponent")
private MyComponent secondaryComponent;
```

```bash
2024-11-14T22:08:28.625+09:00  INFO 75143 --- [spring-web] [           main] o.example.springweb.service.MyService    : MyService initiate. MyComponent org.example.springweb.service.bean_injection.SecondaryComponent
```

- 의도한대로 SecondaryComponent 빈이 주입된다.

++

롬복 Annotation Processor가 필드에 선언된 @Qualifier 애노테이션을 복사하게 하는 방법 → https://ath3nd.wordpress.com/2018/12/13/spring-lombok-or-injection-just-became-a-bit-easier-part-2-of-2/