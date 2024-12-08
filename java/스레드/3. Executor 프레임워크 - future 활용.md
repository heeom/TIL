# Future 활용

### 멀티스레드에서 Future 활용

- 멀티스레드에서 1- 50, 51-100 까지 각각 더하고 결과를 반환받아서 두 결과를 합하는 코드

```java

public class SumTaskMainV2 {

    public static void main(String[] args) throws ExecutionException, InterruptedException {
        SumTask sumTask1 = new SumTask(1, 50);
        SumTask sumTask2 = new SumTask(51, 100);
        ExecutorService executorService = Executors.newFixedThreadPool(2);
        Future<Integer> future1 = executorService.submit(sumTask1);
        Future<Integer> future2 = executorService.submit(sumTask2);

        Integer sum1 = future1.get(); // 블로킹 2초 대기
        Integer sum2 = future2.get(); // 블로킹 즉시 반환 (위에서 main스레드가 대기하는 동안 완료)

        log("task1.result : " + sum1);
        log("task2.result : " + sum2);

        int sum = sum1 + sum2;
        log("sumAll = " + sum);
        executorService.close();
        log("== End ==");
    }

    static class SumTask implements Callable<Integer> {
        int startValue;
        int endValue;

        public SumTask(int startValue, int endValue) {
            this.startValue = startValue;
            this.endValue = endValue;
        }

        @Override
        public Integer call() throws InterruptedException { // checked 예외를 던질 수 있다
            log("작업시작");
            Thread.sleep(2000);
            int sum = 0;
            for (int i = startValue; i <= endValue; i++) {
                sum += i;
            }
            log("작업완료 sum = " + sum);

            return sum;
        }
    }
}

```

- Future<Integer> future1 = executorService.submit(sumTask1);
    - 요청(main) 스레드는 즉시 Future 반환 받음 → 작업 스레드1 은 task1을 수행
- Future<Integer> future2 = executorService.submit(sumTask2);
    - 요청(main) 스레드는 즉시 Future 반환 받음 → 작업 스레드2 은 task2을 수행
- 요청 스레드는 task1, task2를 동시에 요청 가능하다. → 두 작업은 동시에 수행됨
- Integer sum1 = future1.get(); // 블로킹
    - 요청 스레드는 get() 호출하며 대기 → 작업 스레드1이 작업을 진행하는 2초간 대기 → 결과 받음
- Integer sum2 = future2.get(); // 블로킹
    - 이후에 future2.get() 호출하며 즉시 결과를 받음
        - 작업 스레드는 main 스레드가 대기하는 2초간 작업을 완료했음
        - 거의 즉시 결과를 반환함

- Future를 잘못 활용한 예1

```java
Future<Integer> future1 = executorService.submit(sumTask1); // 작업전달
Integer sum1 = future1.get(); // 블로킹 2초대기

Future<Integer> future2 = executorService.submit(sumTask2);
Integer sum2 = future2.get(); // 블로킹 2초대기
```

- Future를 잘못 활용한 예2

```java
Integer sum1 = executorService.submit(sumTask1).get(); // 2초 대기
Integer sum2 = executorService.submit(sumTask2).get(); // 2초 대기
```

- 요청 스레드는 Future를 받음으로써 대기하지 않고, 다른 작업을 수행할 수 있다.
    - Future를 제대로 사용하는 경우 task1, task2를 동시에 요청할 수 있고, 두 작업을 동시에 요청했으므로 작업을 동시에 수행할 수 있다.
- 모든 작업 요청이 끝난 다음에 요청스레드가 필요할때 Future.get()을 호출해서 최종 결과를 받을 수 있다.
- Future는 요청 스레드를 블로킹(WAITING) 상태로 만들지 않고, 요청을 모두 수행할 수 있게 해준다. → ExecutorService는 결과를 반환하지 않고(결과를 받을 때까지 대기하지 않고) Future를 반환한다.

### Future의 다양한 기능

- Future 취소

    ```java
    public class FutureCancelMain {
    
        private static boolean mayInterruptIfRunning = true;
    
        public static void main(String[] args) {
            ExecutorService executorService = Executors.newFixedThreadPool(1);
            Future<String> future = executorService.submit(new MyTask());
            log("future.state " + future.state());
    
            // 일정 시간 후 취소 시도
            sleep(3000);
    
            // cancel() 호출
            log("future.cancel(" + mayInterruptIfRunning + ") 호출");
            boolean cancel = future.cancel(mayInterruptIfRunning);
            log("cancel : " + mayInterruptIfRunning + " result : " + cancel);
    
            try {
                log("Future result : " + future.get());
            } catch (CancellationException e) {
                log("Future 이미 취소");
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
    
        }
        static class MyTask implements Callable<String> {
    
            @Override
            public String call() throws Exception {
    
                try {
                    for (int i = 0; i < 10; i++) {
                        log("작업중 : " + i);
                        Thread.sleep(1000); // 1초 동안 sleep
                    }
                } catch (InterruptedException e) {
                    log("인터럽트 발생");
                    return "InterruptedException";
                }
                return "Completed";
            }
        }
    }
    
    ```

    ```Bash
    > Task :FutureCancelMain.main()
    16:11:24.308 [     main] future.state RUNNING
    16:11:24.308 [pool-1-thread-1] 작업중 : 0
    16:11:25.317 [pool-1-thread-1] 작업중 : 1
    16:11:26.319 [pool-1-thread-1] 작업중 : 2
    16:11:27.317 [     main] future.cancel(true) 호출
    16:11:27.319 [pool-1-thread-1] 인터럽트 발생
    16:11:27.334 [     main] cancel : true result : true
    16:11:27.334 [     main] Future 이미 취소
    ```

    - future.cancel(true) : 현재 진행중인 작업도 같이 취소
    - future.cancel(false) : 현재 진행중인 작업은 계속 진행
    - 두 경우 모두 Future는 취소되었기 때문에 결과값은 받을 수 없다.

### Future 예외

```java
public class FutureExceptionMain {

    public static void main(String[] args) {
        ExecutorService executorService = Executors.newFixedThreadPool(1);
        Future<Integer> future = executorService.submit(new ExCallable());
        sleep(1000); // 잠시 대기
        try {
            log("future.get() 호출 시도, future.state() : " + future.state());
            Integer result = future.get();
            log("result value = " + result);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } catch (ExecutionException e) { // 실행 예외 call() 내부에서 예외가 발생했을때 발생하는 예외
            log("e : " + e);
            Throwable cause = e.getCause();
            log("cause : " + cause);
        }
    }

    static class ExCallable implements Callable<Integer> {
        @Override
        public Integer call() throws Exception {
            log("Callable 실행 예외 발생");
            throw new IllegalStateException("runtime ex");
        }
    }
}
```

```bash
> Task :FutureExceptionMain.main()
16:34:20.569 [pool-1-thread-1] Callable 실행 예외 발생
16:34:21.549 [     main] future.get() 호출 시도, future.state() : FAILED
16:34:21.550 [     main] e : java.util.concurrent.ExecutionException: java.lang.IllegalStateException: runtime ex
16:34:21.550 [     main] cause : java.lang.IllegalStateException: runtime ex
```

- get() 호출 → Future의 상태가 FAILED면 ExecutionException 예외를 던짐
    - 이예외는 Future에서 저장해둔 IllegalStateException 을 포함하고 있음
    - e.getCause()를 호출하면 원본 예외를 받을 수 있음

## ExecutorService 작업 컬렉션 처리

- invokeAll()

```java
ExecutorService executorService = Executors.newFixedThreadPool(10);
        CallableTask task1 = new CallableTask("task1", 1000);
        CallableTask task2 = new CallableTask("task2", 2000);
        CallableTask task3 = new CallableTask("task3", 3000);
        List<CallableTask> tasks = List.of(task1, task2, task3);
        List<Future<Integer>> futures = executorService.invokeAll(tasks);
        for (Future<Integer> future : futures) {
            Integer value = future.get();
            log("value = " + value);
        } // task1,2,3 작업 모두 완료될때까지 기다림
        // task3가 가장 오래 걸리는 작업(3000ms)이므로, 전체 실행 시간은 3000ms가 된다.
        executorService.close();
```

- 세 개의 CallableTask(task1, task2, task3)가 invokeAll 메서드를 통해 동시에 실행 요청된다
    - invokeAll 메서드는 **모든 작업이 완료될 때까지 메인 스레드를 블로킹한다**
    - 모든 task가 완료될때까지 기다림

- invokeAny()

```java
ExecutorService executorService = Executors.newFixedThreadPool(10);
        CallableTask task1 = new CallableTask("task1", 1000);
        CallableTask task2 = new CallableTask("task2", 2000);
        CallableTask task3 = new CallableTask("task3", 3000);

        List<CallableTask> tasks = List.of(task1, task2, task3);
        Integer value = executorService.invokeAny(tasks); 

        log("value = " + value);
        executorService.close();
```

- task1,2,3 중에 하나라도 먼저 완료되면 리턴하고, 나머지 작업은 취소 처리