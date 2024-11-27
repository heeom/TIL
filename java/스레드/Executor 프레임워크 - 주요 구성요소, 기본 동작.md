## Executor 프레임워크의 주요 구성요소

### `Executor`, `ExecutorService` 인터페이스

- ExecutorService의 기본 구현체 : ThreadPoolExecutor

### ExecutorService - ThreadPoolExecutor

``` bash
ExecutorService executorService = new ThreadPoolExecutor(2,2,0, TimeUnit.MILLISECONDS, new LinkedBlockingDeque<>());
        log("== 초기 상태 ==");
        printState(executorService);
        executorService.execute(new RunnableTask("taskA"));
        executorService.execute(new RunnableTask("taskB"));
        executorService.execute(new RunnableTask("taskC"));
        executorService.execute(new RunnableTask("taskD"));
        log("== 작업 수행 중 ==");
        printState(executorService);
```

```bash
> Task :ExecutorBasicMain.main()
22:11:35.043 [     main] == 초기 상태 ==
22:11:35.062 [     main] [pool=0, active = 0, queueTasks = 0, completedTask = 0
22:11:35.064 [     main] == 작업 수행 중 ==
22:11:35.064 [     main] [pool=2, active = 2, queueTasks = 2, completedTask = 0
22:11:35.064 [pool-1-thread-2] taskB 시작
22:11:35.064 [pool-1-thread-1] taskA 시작
22:11:35.168 [pool-1-thread-2] taskB 완료
22:11:35.168 [pool-1-thread-1] taskA 완료
22:11:35.168 [pool-1-thread-2] taskC 시작
22:11:35.169 [pool-1-thread-1] taskD 시작
22:11:35.274 [pool-1-thread-2] taskC 완료
22:11:35.274 [pool-1-thread-1] taskD 완료
22:11:38.067 [     main] == 작업 수행 완료 ==
22:11:38.068 [     main] [pool=2, active = 0, queueTasks = 0, completedTask = 4
22:11:38.070 [     main] == shutdown ==
22:11:38.071 [     main] [pool=0, active = 0, queueTasks = 0, completedTask = 4
```

- ExecutorService의 구현체 ThreadPoolExecutor 구성요소
    - 스레드풀 : 스레드 관리
    - BlockingQueue : 작업 보관 (생산자 소비자 문제 때문에 BlockingQueue 사용)
- 생산자 - main 스레드
    - executorService.execute(new RunnableTask("taskA")); 호출
    - RunnableTask("taskA") 인스턴스 → BlockingQueue에 작업 보관
- 소비자 - 스레드 풀에 잇는 스레드
    - 생산자 스레드가 작업을 BlockingQueue에 보관한 다음 스레드 풀에 있던 소비자 중에 하나가 BlockingQueue에 있는 작업을 받아서 처리

### ThreadPoolExecutor 생성자

- corePoolSize : 스레드 풀에서 관리되는 기본 스레드 수
- maximumPoolSize : 스레드 풀에서 관리되는 최대 스레드 수
- keepAliveTime, TimeUnit unit : 기본 스레드 수를 초과해서 만들어진 스레드가 생존할 수 있는 대기 시간. (이 시간 동안 처리할 작업이 없으면 초과스레드는 제거됨)
- BlockingQueue : 작업을 보관할 블로킹 큐

```bash
new ThreadPoolExecutor(2,2,0, TimeUnit.MILLISECONDS, new LinkedBlockingDeque<>());
```

- corePoolSize = 2, maximumPoolSize=2, 블로킹 큐는 무한대로 저장 가능

```bash
22:11:35.043 [     main] == 초기 상태 ==
22:11:35.062 [     main] [pool=0, active = 0, queueTasks = 0, completedTask = 0
```

- 초기에는 스레드 풀에 스레드가 0개

### executorService.execute(작업)

- main 스레드가 executorService.execute A, B, C, D 호출
- main 스레드는 작업을 큐에 보관하고 바로 다음 코드 수행
- task A, B, C, D 요청이 블로킹 큐에 들어감
    - 최초 작업이 큐에 들어오면 작업을 처리하기 위해 스레드 생성
- 작업이 들어올때마다 corePoolSize의 크기까지 스레드를 만든다.
- corePoolSize까지 스레드가 생성되고 나면 이후에는 만들어진 스레드 재사용

```bash
22:11:35.064 [     main] == 작업 수행 중 ==
22:11:35.064 [     main] [pool=2, active = 2, queueTasks = 2, completedTask = 0
```

- 스레드 풀에 스레드 `pool=2`
- 작업 수행 중인 스레드 `active = 2`
- 큐에 대기중인 작업 `queueTasks = 2`
- 완료된 작업 `completedTask = 0`

### 스레드 작업완료 → 반납

```bash
22:11:35.064 [pool-1-thread-2] taskB 시작
22:11:35.064 [pool-1-thread-1] taskA 시작
22:11:35.168 [pool-1-thread-2] taskB 완료
22:11:35.168 [pool-1-thread-1] taskA 완료
22:11:35.168 [pool-1-thread-2] taskC 시작
22:11:35.169 [pool-1-thread-1] taskD 시작
22:11:35.274 [pool-1-thread-2] taskC 완료
22:11:35.274 [pool-1-thread-1] taskD 완료
```

- 작업완료되면 스레드 풀에 스레드 반납 → 반납된 스레드는 WAITING 상태로 스레드 풀에 대기
    - `[pool-1-thread-2] taskB 완료`
- 반납된 스레드는 재사용된다
    - `[pool-1-thread-2] taskC 시작`

### shutdown

```bash
22:11:38.070 [     main] == shutdown ==
22:11:38.071 [     main] [pool=0, active = 0, queueTasks = 0, completedTask = 4
```

- close() 호출하면 ThreadPoolExecutor가 종료됨
- 스레드 풀에 대기하는 스레드도 제거됨