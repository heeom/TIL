## 우선순위큐

---

- 특정 조건에 따라 우선순위가 가장 높은 엘리먼트가 가장 먼저 추출되는 자료형
- ex) [1,4,5,3,2] → [1,2,3,4,5] 순으로 추출됨

```java
PriorityQueue<Integer> priorityQueue = new PriorityQueue<>((o1, o2) -> {
            if (o1 == o2) {
                return 0;
            } else if (o1 > o2) {
                return 1;
            }
            return -1;
        });
```