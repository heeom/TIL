# 동시성문제해결 - Redis 사용 
## 분산락 구현시 사용할 수 있는 Redis 라이브러리

### Lettuce
    - key:value
    - retry로직 개발자가 직접 작성해줘야함
    - 장점
        - 구현이 간단
        - spring data redis 를 이용하면 lettuce 가 기본이기때문에 별도의 라이브러리를 사용하지 않아도 된다.
    - 단점
        - spin lock 방식이기때문에 동시에 많은 스레드가 lock 획득 대기 상태라면 redis 에 부하가 갈 수 있다.
        - 락 획득 재시도 사이에 텀을 줘야 함
### Redisson
    - pub-sub 기반
    - retry 로직 작성 안해도 됨
    - 장점
        - 락 획득 재시도를 기본으로 제공한다.
        - pub-sub 방식으로 구현이 되어있기 때문에 lettuce 와 비교했을 때 redis 에 부하가 덜 간다.
    - 단점
        - 별도의 라이브러리를 사용해야해서 라이브러리 사용법을 알아야함
        - 구현이 복잡
- 재시도가 필요하지 않은 lock은 lettuce를 재시도가 필요한 경우에는 redisson을 사용하자

## Docker로 redis 컨테이너 띄우기

```bash
docker pull redis

docker run --name myredis -d -p 6379:6379 redis
```

> 💡  redis-cli 명령어
>

```bash
# redis 서버 상태확인
redis-cli ping

# 실시간으로 어떤 작업이 있는지 모니터링
redis-cli monitor

```

## Spring Data Redis 의존성 추가

```groovy
implementation 'org.springframework.data:spring-data-redis'
// spring boot version 3.3.3 기준 lettuce 의존성도 추가해줘야한다.
implementation 'io.lettuce:lettuce-core:6.3.2.RELEASE'
```

- implementation 'org.springframework.data:spring-data-redis' 의존성만 추가해줬더니 `java.lang.ClassNotFoundException: io.lettuce.core.AbstractRedisClient`  ClassNotFoundException 예외가 발생해서 lettuce 의존성도 추가

## Lettuce를 작성하여 재고 감소로직 작성하기

- redis-cli로 먼저 lock 획득과 해제 과정을 확인해보자

```bash
docker exec -it 1f73703b2ece redis-cli

127.0.0.1:6379> setnx 1 lock # key value
(integer) 1
127.0.0.1:6379> setnx 1 lock # 중복이라 실패
(integer) 0
127.0.0.1:6379> del 1 # key 1을 삭제하고
(integer) 1
127.0.0.1:6379> setnx 1 lock # 다시 set하면 성공
(integer) 1
```

- 위와 같이 lock 획득과 해제를 위해 RedisLockRepository 구현

```java
@Component
public class RedisLockRepository {

    private final RedisTemplate<String, String> redisTemplate;

    public RedisLockRepository(RedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    // 락 획득 시도
    // setIfAbsent : Redis의 SET key value NX EX (키가 존재하지 않을때만 값을 설정한다)
    public Boolean lock(Long key) {
        return redisTemplate
                .opsForValue()
                .setIfAbsent(generateKey(key), "lock", Duration.ofMillis(3_000));
    }

    private String generateKey(Long key) {
        return key.toString();
    }
    
    // 락 해제
    public Boolean unlock(Long key) {
        return redisTemplate.delete(generateKey(key));
    }
}
```

```java
@Component
public class LettuceLockStockFacade {

    private final RedisLockRepository redisLockRepository;;
    private final StockService stockService;

    public LettuceLockStockFacade(RedisLockRepository redisLockRepository, StockService plainStockService) {
        this.redisLockRepository = redisLockRepository;
        this.stockService = plainStockService;
    }

    public void decrease(Long id, Long quantity) throws InterruptedException {
        // lock 획득 성공할떄까지 재시도
        while(!redisLockRepository.lock(id)) {
            Thread.sleep(100);
        }

        try {
            // 재고감소
            stockService.decrease(id, quantity);
        } finally {
            // 완료하면 락 해제
            redisLockRepository.unlock(id);
        }
    }
}
```

- 동시에 100개의 재고 감소를 요청하는 테스트

```java
@Test
    void 동시에_100개의_요청() throws InterruptedException {
        int thread = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(32);
        CountDownLatch countDownLatch = new CountDownLatch(thread);

        for (int i = 0; i < thread; i++) {
            executorService.submit(() -> {
                try {
                    lettuceLockStockFacade.decrease(1L, 1L);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                } finally {
                    countDownLatch.countDown();
                }
            });
        }
        countDownLatch.await();
        Stock stock = stockRepository.findById(1L).orElseThrow();
        assertEquals(0, stock.getQuantity());
    }
```

- Redis 로그를 보면 락 획득과 해제가 이루어지고 있다

```java
1725160036.168231 [0 192.168.65.1:49837] "HELLO" "3"
1725160036.178361 [0 192.168.65.1:49837] "CLIENT" "SETINFO" "lib-name" "Lettuce"
1725160036.178430 [0 192.168.65.1:49837] "CLIENT" "SETINFO" "lib-ver" "6.3.2.RELEASE/8941aea"
1725160036.327563 [0 192.168.65.1:49837] "SET" "1" "lock" "EX" "3" "NX"
1725160036.361421 [0 192.168.65.1:49837] "DEL" "1"
1725160036.364858 [0 192.168.65.1:49837] "SET" "1" "lock" "EX" "3" "NX"
1725160036.396354 [0 192.168.65.1:49837] "DEL" "1"
1725160036.398618 [0 192.168.65.1:49837] "SET" "1" "lock" "EX" "3" "NX"
1725160036.421412 [0 192.168.65.1:49837] "DEL" "1"
1725160036.423736 [0 192.168.65.1:49837] "SET" "1" "lock" "EX" "3" "NX"
```

## Redisson을 사용하여 재고 감소로직 작성하기

- Redisson은 자신이 점유하고 있는 락을 해제할 때 채널에 메세지를 보내줌으로써 락 획득을 대기하고 있는 다른 스레드들에게 락획득을 하라고 알려줌 → 대기하고 있는 스레드들은 메세지를 받았을때 락획득을 시도함
    - lettuce는 계속해서 락획득을 시도하는 반면 Redisson은 메세지를 받았을때만 락획득을 시도하기때문에 redis의 부하를 줄여주게 된다.

- 먼저 redis-cli로 확인해보자
    - ch1 채널 구독

        ```bash
        	127.0.0.1:6379> subscribe ch1
        1) "message"
        2) "ch1"
        3) "hello"
        ```

    - ch1 채널로 메세지 전송

        ```bash
        127.0.0.1:6379> publish ch1 hello
        ```


- Redisson은 락 획득과 해제하는 기능을 RedissonClient에서 제공하기 때문에 직접 구현하지 않아도 된다.

```java
@Component
public class RedissonLockStockFacade {

    private static final Logger log = LoggerFactory.getLogger(RedissonLockStockFacade.class);

    private RedissonClient redissonClient;

    private StockService stockService;

    public RedissonLockStockFacade(RedissonClient redissonClient, StockService plainStockService) {
        this.redissonClient = redissonClient;
        this.stockService = plainStockService;
    }

    public void decrease(Long id, Long quantity) {

        RLock lock = redissonClient.getLock(id.toString());

        try {
            boolean triedLock = lock.tryLock(10, 1, TimeUnit.SECONDS);
            if (!triedLock) {
                log.info("tried lock failed ");
                return;
            }
            stockService.decrease(id, quantity);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            lock.unlock();
        }
    }
}
```

- `boolean tryLock(long waitTime, long leaseTime, TimeUnit unit) throws InterruptedException;`
    - `waitTime` : 락 획득을 위해 대기할 최대 시간, 대기시간이 지나면 락 획득을 포기하고 false 반환
    - `leaseTime` : 락을 획득한 후 자동으로 해제되끼까지의 시간 설정. (leaseTime이 0이거나 음수면 수동으로 해제해줘야 한다)
    - `unit` : `waitTime`과 `leaseTime`에 대한 시간 단위를 지정

```java
@Test
    void 동시에_100개의_요청() throws InterruptedException {
        int thread = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(32);
        CountDownLatch countDownLatch = new CountDownLatch(thread);

        for (int i = 0; i < thread; i++) {
            executorService.submit(() -> {
                try {
                    redissonLockStockFacade.decrease(1L, 1L);
                } finally {
                    countDownLatch.countDown();
                }
            });
        }
        countDownLatch.await();
        Stock stock = stockRepository.findById(1L).orElseThrow();
        assertEquals(0, stock.getQuantity());
    }
```

reference : 
https://spring.io/projects/spring-data-redis