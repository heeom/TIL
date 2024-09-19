## Collections 정렬 관련 메서드

```java
List<Integer> list = new ArrayList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);

        Integer max = Collections.max(list); // 최대값
        Integer min = Collections.min(list); // 최소값

        Collections.shuffle(list); // 컬렉션을 랜덤하게 섞는다.
        Collections.sort(list); // 정렬기준으로 정렬
        Collections.reverse(list); // 정렬기준의 반대로 정렬
```

## Collection 생성

```java
public static void main(String[] args) {
        // 편리한 불변 컬렉션 생성
        List<Integer> list = List.of(1, 2, 3);
        Set<Integer> set = Set.of(1, 2, 3);
        Map<Integer, String> map = Map.of(1, "one", 2, "two", 3, "three");
        System.out.println("list : " + list.getClass());
        // list : class java.util.ImmutableCollections$ListN
        // 컬렉션을 변경하려고 하면 예외가 발생한다.
    }
```

## 불변컬렉션 생성

```java
public class ImmutableMain {

    public static void main(String[] args) {
        // 불변 리스트 생성
        List<Integer> list = List.of(1, 2, 3);

        // 가변리스트로 변환
        ArrayList<Integer> mutableList = new ArrayList<>(list);
        mutableList.add(4);
        System.out.println(mutableList);

        // 다시 불변 리스트로 변경
        Collection<Integer> immutableList = Collections.unmodifiableCollection(mutableList);
        System.out.println("unmodifiableList : " + immutableList.getClass());
//        immutableList.add(5); // 예외 발생 : Exception in thread "main" java.lang.UnsupportedOperationException
    }
}
```

- 불변리스트(`of`메서드로 생성) → 가변리스트로 전환(`new ArrayList<>()` )
- 가변리스트 → 불변리스트로 전환(`Collections.unmodifiableList()`)

## EmptyList 생성

```java
public class EmptyListMain {

    public static void main(String[] args) {
        // empty 가변 리스트
        List<Integer> list1 = new ArrayList<>();
        List<Integer> list2 = new ArrayList<>();

        // empty 불변 리스트
        List<Integer> list3 = Collections.emptyList(); // java 5
        List<Integer> list4 = List.of(); // java 9

        System.out.println("list3 = " + list3.getClass());
        System.out.println("list4 = " + list4.getClass());
        // list3 = class java.util.Collections$EmptyList
				// list4 = class java.util.ImmutableCollections$ListN

        // 완전 불변 리스트 아님
        // 고정된 크기를 가지지만, 요소 변경은 가능, set을 통해 변경은 가능하지만 add(), remove()로 길이변경은 불가능
        List<Integer> list5 = Arrays.asList(1, 2, 3); // java 1.2 : 배열 -> List

        Integer[] arr = {1,2,3,4,5};
        List<Integer> arr1 = List.of(arr); // 새로운 리스트를 생성
        List<Integer> arr2 = Arrays.asList(arr); // 리스트 생성시 배열의 참조값을 그대로 사용 -> 리스트 생성하는 비용이 더 적음 / 배열의 크기가 아주 크다면 Arrays.asList가 나을 수도 있음
    }
}
```

- 불변 empty List 생성하는 방법
    - `Collections.emptyList()` : java5 부터 제공되는 기능
    - `List.of()` : java9부터 제공되는 기능 (권장)
- Arrays.asList()
    - java 1.2부터 지원했음
    - 크기는 고정, 요소는 변경 가능 (기존위치에 있는 요소들은 변경가능)
- 대부분 List.of()를 사용하는 것이 권장되지만 다음과 같은 경우 Arrays.asList()를 선택할 수 있다.
    - 리스트 내부 요소를 변경해야하는 경우
    - 하위호환성 : java9 이전 버전에서 작업해야 하는 경우

## 멀티스레드 동기화

```java
public class SyncMain {
    public static void main(String[] args) {
        ArrayList<Integer> list = new ArrayList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);

        System.out.println("list class :" + list.getClass());
        List<Integer> synchronizedList = Collections.synchronizedList(list);
        System.out.println("synchronizedList class :" + synchronizedList.getClass());
        // list class :class java.util.ArrayList
        // synchronizedList class :class java.util.Collections$SynchronizedRandomAccessList

    }
}
```

- Collections.synchronizedList : 멀티스레드 상황에서 동기화문제가 발생하지 않는 안전한 리스트로 만들 수 있다.
- 동기화 작업으로 일반 리스트보다 성능은 더 느리다.