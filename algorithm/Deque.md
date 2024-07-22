## Deque?

- Double-Ended Queue
- 양 쪽 끝을 모두 추출할 수 있음
    - 양쪽 끝에서 삽입과 삭제를 모두 처리할 수 있다.
    - 스택과 큐의 모든 연산을 지원한다.
- 큐를 일반화한 형태의 추상 자료형
- Deque의 구현은 배열이나 Linked List 모두 가능하지만 Doubly Linked List(이중 연결 리스트)로 구현하는 것이 가장 좋음 (head, tail 포인터 두개를 가짐)
- 자바에서 Deque를 구현하는 자료형은 Queue와 마찬가지로 인터페이스이며, Queue를 확장해서 정의하고 있다.
    - 실제 구현은 LinkedList or ArrayDeque
    - LinkedList : 이중 연결 리스트로 구현 되어 있음

    ```java
    Deque<Integer> deque = new LinkedList<>();
    ```


## Java에서 Stack 자료형은 사용하지 않는다

- Stack 클래스는 자바ㅏ1.2 이전, 싱글 코어 시절에 나온 자료형으로 모든 작업에 Lock 이 수행되는 Vector라는 자료형을 기반으로 함
    - 여러 읽기 작업도 동시에 수행할 수 없고, 차례대로 읽어야 함
- Vector → ArrayList로 개선되었고, Stack 대신 Deque 자료형을 권장한다.
    - Deque
        - 인터페이스
        - LinkedList, ArrayDeque 구현체로 함

    ```java
    Deque<Integer> stack = new ArrayDeque<>();
    ```

- 스레드 safe가 필요한 경우
    - 스레드 safe?
        - 멀티 스레드 프로그래밍에서 어떤 함수나 변수, 객체를 여러 스레드에서 동시에 접근해도 프로그램 실행에 문제가 없는 것
        - 스레드 safe하지 않다면 → 어떤 스레드가 자료형에 값을 삽입하던 도중에 동시에 다른 스레드가 접속해서 삽입 작업이 완료되기 전에 값을 삭제할 수 도 있음
    - 스레드 safe가 필요한 경우 `LinkedBlockigDeque` , `ConcurrentLinkedDeque` 를 사용하면 된다.