```java
    
    @Test
    public void 동시에_100개_재고_감소_요청() throws InterruptedException {

        int threadCount = 100; // 생성할 스레드 개수 설정

        // 사용할 스레드 관리
        // 고정 스레드풀 생성(동시에 최대 32개의 스레드만 실행되도록 제한)
        ExecutorService executorService = Executors.newFixedThreadPool(32);
        // 다른 스레드에서 특정 작업이 완료될 때까지 대기 -> 100개 스레드가 모두 작업을 완료할때까지 대기
        CountDownLatch latch = new CountDownLatch(threadCount);

        for (int i = 0; i < threadCount; i++) {
            executorService.submit(() -> {
                try {
                    stockService.decrease(1L, 1L);
                } finally {
                    // 현재 스레드의 작업 끝
                    latch.countDown();
                }
            });
        }

        latch.await(); // 스레드 대기
        Stock stock = stockRepository.findById(1L).orElseThrow();
        assertEquals(0, stock.getQuantity());
    }
```

위 테스트는 100개의 스레드에서 동시에 재고를 1씩 감소시키는 코드이다. 이 테스트 코드는 레이스 컨디션이 발생하기 때문에 실패한다.

레이스 컨디션이란?

둘 이상의 Thread가 공유 데이터에 엑세스할 수 있고 동시에 변경을 하려고 할때 발생하는 문제를 말한다.

해결 방법은 하나의 스레드가 작업을 완료한 이후에 다른 스레드가 데이터에 접근가능하도록 하면 된다.

먼저 자바의 synchronized를 사용해보자.

```java
@Transactional
public synchronized void decrease(Long id, Long quantity) {
        Stock stock = stockRepository.findById(id).orElseThrow(EntityNotFoundException::new);
        stock.decrease(quantity);
        stockRepository.saveAndFlush(stock);
    }
```

synchronized를 사용해도 해당 테스트 코드의 결과는 실패하는데, 이유는 @Transactional의 동작 방식에 있다. 작업 중인 스레드가 커밋되기 전에 다른 스레드가 decrease 메서드에 접근하기 때문에 여전히 문제가 발생한다. @Transactional 을 주석 처리하고 다시 테스트를 실행하면 성공한다.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/72038517-8ad4-4bad-a50e-fa0deed31c0b/01394349-ed66-4f5c-b959-e2a100e5eb9b/image.png)

Synchronized를 사용했을 때 문제점도 알아보자.

Java의 Synchronized는 하나의 프로세스 안에서만 보장이 된다.

서버가 한 대만 있을 때는 한대의 서버만 데이터에 접근을 해서 괜찮지만, 서버가 한개 이상일 경우 여러개의 서버에서 데이터에 동시 접근 할 수 있게 된다.