# Future


### Future 와 Runnable 비교

|  | Runnable | Callable |
| --- | --- | --- |
| 반환 타입 | void run() | V call() |
| 예외 선언 | 예외 선언 되어 있지 않으므로 자식은 checked 예외를 던질 수 없다 | V call() throws Exception; 예외 선언 되어 있음 

```java
package com.example.thread.executor.future;

import java.util.Random;
import java.util.concurrent.*;

import static com.example.util.MyLogger.log;
import static com.example.util.ThreadUtils.sleep;

public class CallableMainV1 {

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        ExecutorService executorService = Executors.newFixedThreadPool(1);
        Future<Integer> future = executorService.submit(new MyCallable()); // MyCallable 인스턴스가 블로킹 큐에 전달 -> 스레드풀의 스레드 중 하나가 작업 실행
        Integer result = future.get();
        log("result value = " + result);
        executorService.close();
    }
    
    static class MyCallable implements Callable<Integer> { // 반환할 제네릭 타입 : Integer

        @Override
        public Integer call() throws Exception {
            log("Callable 시작");
            sleep(2000);
            int value = new Random().nextInt(100);
            log("create value = " + value);
            log("Callable 완료 ");
            return value; // 결과를 별도의 필드에 보관하지 않고 반환
        }
    }
}

```

- `Future<Integer> future = executorService.submit(new MyCallable());`
    - MyCallable 인스턴스가 블로킹 큐에 전달 → 스레드풀의 스레드 중 하나가 작업 실행 → 작업 결과 반환


### Executor 프레임 워크의 강점

- Runnable 방식보다 훨씬 편리함
    - 스레드를 직접 생성하거나, join()으로 다른 스레드의 작업을 기다릴 필요가 없음

### Future 분석

```java
Future<Integer> future = executorService.submit(new MyCallable()); 
```

- MyCallable 인스턴스가 블로킹 큐에 전달 → 스레드풀의 스레드 중 하나가 작업 실행 → 작업 결과 반환
- submit()이 Future 반환

- MyCallable.call() 메서드는 호출 스레드(main스레드)가 실행 하는게 아니라 스레드 풀의 다른 스레드가 실행하기 때문에 future.get() 호출하는 요청 스레드(main스레드)가 future.get() 을 호출했을 때 2가지 상황으로 나뉜다
    - MyCallable 작업을 처리하는 스레드 풀의 스레드가 작업 완료 O
        - 문제 없음, 결과 반환
    - MyCallable 작업을 처리하는 스레드 풀의 스레드가 작업 완료 X
        - 언제 실행이 완료돼서 결과 반환하는지 알 수 없다
- 즉, 결과를 즉시 리턴 받는 것은 불가능하다 → submit()은 MyCallable의 작업 결과를 반환하는 대신 MyCallable의 결과를 나중에 받을 수 있는 Future 객체를 대신 제공한다.

```java
public class CallableMainV2 {

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        ExecutorService executorService = Executors.newFixedThreadPool(1);
        log("submit() 호출");
        Future<Integer> future = executorService.submit(new MyCallable());
        log("future 즉시 반환, future = " + future);
        log("future.get() [블로킹] 메서드 호출 시작 -> main 스레드 WAITING");

        Integer result = future.get(); // 블로킹

        log("future.get() [블로킹] 메서드 호출 시작 -> main 스레드 RUNNABLE");

        log("result value = " + result);
        log("future 완료, future = " + future);
        executorService.close();
    }
    
    static class MyCallable implements Callable<Integer> { // 반환할 제네릭 타입

        @Override
        public Integer call() throws Exception {
            log("Callable 시작");
            sleep(2000);
            int value = new Random().nextInt(100);
            log("create value = " + value);
            log("Callable 완료 ");
            return value;
        }
    }
}
```

```bash
> Task :CallableMainV2.main()
20:22:59.684 [     main] submit() 호출
20:22:59.687 [pool-1-thread-1] Callable 시작
20:22:59.688 [     main] future 즉시 반환, future = java.util.concurrent.FutureTask@45ee12a7[Not completed, task = com.example.thread.executor.future.CallableMainV2$MyCallable@135fbaa4]
20:22:59.688 [     main] future.get() [블로킹] 메서드 호출 시작 -> main 스레드 WAITING
20:23:01.704 [pool-1-thread-1] create value = 62
20:23:01.705 [pool-1-thread-1] Callable 완료 
20:23:01.706 [     main] future.get() [블로킹] 메서드 호출 시작 -> main 스레드 RUNNABLE
20:23:01.706 [     main] result value = 62
20:23:01.707 [     main] future 완료, future = java.util.concurrent.FutureTask@45ee12a7[Completed normally]
```

- Future<Integer> future = executorService.submit(new MyCallable());
- [Future 생성 및 반환] executorService.submit(Task);
    - Future 인터페이스의 구현체 FutureTask 생성
    - 생성한 Future 객체에 Task(MyCallable)의 인스턴스를 보관한다.
    - Future는 내부에 task의 작업 완료 여부와 작업의 결과값을 가진다.
        - `FutureTask@45ee12a7[Not completed, task = com.example.thread.executor.future.CallableMainV2$MyCallable@135fbaa4]`
        - submit을 호출시에 task가 바로 블로킹 큐에 담기는게 아니라 task를 감싸고 있는 Future가 대신 블로킹 큐에 담긴다.
- 작업을 전달할 때 생성된 Future는 즉시 반환된다.
    - `Future<Integer> future = executorService.submit(new MyCallable());`
    - Future를 즉시 반환하기 때문에 요청스레드는 대기하지 않고, 다음코드를 바로 호출한다.
- [Future 실행] `[pool-1-thread-1] Callable 시작`
    - 블로킹 큐에 있는 Future를 꺼내서 스레드 풀의 `thread-1` 이 작업을 시작한다.
    - `thread-1` 은 FutureTask의 run() 실행 → run()이 task의 call() 호출 → 결과를 받아서 처리한다.
        - FutureTask.run() → MyCallable.call()
- [블로킹] `future.get()`
    - 스레드가 작업을 아직 처리중이면, Future도 완료 상태가 아니다.
    - 요청 스레드가 future.get()을 호출하면 Future가 완료 상태가 될때까지 대기한다.
        - 이때 요청 스레드상태는 RUNNABLE → WAITING 이 된다.
        - 스레드가 어떤 결과를 얻기위해 대기하는것을 블로킹이라고 한다. ex) thread.join(), future.get()
- [Future 완료]

    ```bash
    20:23:01.704 [pool-1-thread-1] create value = 62
    20:23:01.705 [pool-1-thread-1] Callable 완료 
    20:23:01.706 [     main] future.get() [블로킹] 메서드 호출 시작 -> main 스레드 RUNNABLE
    ```

    - task 작업 완료 → Future에 작업의 결과를 담고 Future 상태 완료로 변경
    - Future를 실행한 스레드1이 요청한 스레드를 깨움
    - 이때 요청 스레드는 WAITING → RUNNABLE 상태가 됨

```bash
20:23:01.707 [     main] future 완료, future = java.util.concurrent.FutureTask@45ee12a7[Completed normally]
```

- 요청스레드 (main)
    - RUNNABLE 상태
    - 완료상태의 Future에게서 결과를 반환 받음
- pool-1-thread-1
    - 스레드풀로 반환
    - RUNNABLE → WAITING