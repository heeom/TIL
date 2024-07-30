## 그래프

- 객체의 일부 쌍들이 연관되어 있는 객체 집합 구조

## 오일러의 경로

- 모든 간선을 한 번씩 방문하는 유한 그래프
- 모든 정점이 짝수 개의 차수를 갖는다면 모든 다리를 한 번씩만 건너서 도달하는 것이 성립한다.

## 해밀턴 경로

- 각 정점을 한 번씩 방문하는 방향이 있거나 없는 그래프 경로를 말한다.
- 오일러 경로와 차이점
    - 오일러 경로 : 간선을 기준으로 함
    - 해밀턴 경로 : 정점을 기준으로 함
- 해밀턴 경로를 찾는 문제는 최적 알고리즘이 없는 NP-complete 문제이다.
- 해밀턴 순환
    - 해밀턴 경로 중에서도 원래의 출발점으로 돌아오는 경로

## 그래프 순회

- 그래프 탐색이라고도 하며, 그래프의 각 정점을 방문하는 과정
    - DFS : 깊이 우선 탐색
        - 주로 스택, 재귀로 구현한다.
    - BFS : 넓이 우선 탐색
        - 주로 큐로 구현한다.
        - 그래프의 최단 경로를 구하는 문제 등에 사용된다.

## DFS
- 재귀 또는 Stack으로 구현 가능하다.
```java
import java.util.*;

public class Graph {
    private static HashMap<Integer, List<Integer>> graph = new HashMap<>();

    public static void main(String[] args) {
        graph.put(1, Arrays.asList(2,3,4));
        graph.put(2, Arrays.asList(5));
        graph.put(3, Arrays.asList(5));
        graph.put(4, Arrays.asList());
        graph.put(5, Arrays.asList(6,7));
        graph.put(6, Arrays.asList());
        graph.put(7, Arrays.asList(3));
        recursiveDfs(1, new ArrayList<>());
        iterativeDfs(1);
    }
		
		// 재귀로 구현한 DFS
    private static List<Integer> recursiveDfs(int n, List<Integer> visited) {
        visited.add(n);
        for (int next : graph.get(n)) {
            if (!visited.contains(next)) {
                visited = recursiveDfs(next, visited);
            }
        }
        return visited;
    }

		// stack 으로 구현한 DFS
        private static List<Integer> iterativeDfs(int n) {
        List<Integer> visited = new ArrayList<>();
        Deque<Integer> stack = new ArrayDeque<>();

        stack.push(n);

        while (!stack.isEmpty()) {
            n = stack.pop();
            if (!visited.contains(n)) {
                visited.add(n);
                for (int next : graph.get(n)) {
                    stack.push(next);
                }
            }
        }
        return visited;
    }
}
```

## BFS
- queue로 구현가능하다.
```java
private static List<Integer> bfsWithQueue(int n) {
        List<Integer> visited = new ArrayList<>();
        Queue<Integer> queue = new LinkedList<>();
        visited.add(n);
        queue.offer(n);
        while(!queue.isEmpty()) {
            int v = queue.poll();
            for (int next : graph.get(v)) {
                if (!visited.contains(next)) {
                    visited.add(next);
                    queue.offer(next);
                }
            }
        }
        return visited;
    }
```