# 컬렉션 프레임워크 - Comparable, Comparator

## Java의 정렬 방식

- 자바는 초기에는 퀵소트를 사용했다가 지금은 데이터가 작을 때(32개 이하)는 듀얼 피벗 퀵소트(Dual-Pivot QuickSort)를 사용하고, 데이터가 많을 때는 팀소트(TimSort)를 사용한다. 이런 알고리즘은 평균 O(n log n)의 성능 을 제공한다.

## Comparator

- 비교자 : 두 값을 비교할 때 비교 기준을 제공한다.

```java
public interface Comparator<T> {
     int compare(T o1, T o2);
}
```

- o1, o2  두 parameter를 비교해서 결과 값을 반환한다.
    - o1 < o2 → 음수
    - o1 > o2 → 양수
    - o1 == o2 → 0

```java
Integer[] arr = {3,2,1};
Arrays.sort(arr, new DescComparator());
Arrays.sort(arr, new DescComparator().reversed()); // 비교의 결과를 반대로 변경한다.
```

- `Arrays.sort()` 에 Comparator를 넘겨주면, 정렬할때 해당 비교자를 사용한다.
- Comparator를 사용하면 정렬의 기준을 자유롭게 변경할 수 있다.

## Comparable

- Comparable : 비교가능한, 객체에 비교기능을 추가해준다

```java
public interface Comparable<T> {
     public int compareTo(T o);
}
```

- 자기 자신(this)과 넘어온 객체(o)를 비교해서 반환
    - this < o → 음수
    - this > o → 양수
    - this == o → 0

```java
public class MyUser implements Comparable<MyUser> {

    private String id;
    private int age;

    @Override
    public int compareTo(MyUser other) {
        return this.age - other.getAge(); // age 오름차순
    }
}

```

- MyUser가 Comparable 인터페이스 구현
- Comparable을 통해 구현한 순서를 자연순서(Natural Ordering)이라고 함

```java
public static void main(String[] args) {
        MyUser a = new MyUser("a", 30);
        MyUser b = new MyUser("b", 20);
        MyUser c = new MyUser("c", 10);

        MyUser [] users = {a, b, c};
        Arrays.sort(users);
    }
```

```
===========sorted
[MyUser{id='c', age=10}, MyUser{id='b', age=20}, MyUser{id='a', age=30}]
```

- `Arrays.sort(users)` : 객체가 갖고 있는 Comparable 인터페이스의 `compareTo` 를 사용해서 비교한다. → MyUser의 자연적인 순서를 사용

## 다른방식으로 정렬?

- 객체가 갖고 있는 Comparable 기본 정렬이 아니라 다른 정렬을 사용하고 싶다면 어떻게 해야할까?
    - Comparator 인터페이스를 사용해서 다른 정렬 방식을 구현하고, Arrays.sort() 에 구현한 클래스를 넘겨서 원하는 정렬 방식을 적용할 수 있다.

```java
public class IdComparator implements Comparator<MyUser> {

    @Override
    public int compare(MyUser o1, MyUser o2) {
        return o1.getId().compareTo(o2.getId());
    }
}
```

```java
Arrays.sort(users, new IdComparator());
```

- 기본 정렬이 아니라 정렬 방식을 지정하고 싶다면 `Arrays.sort` 의 인수로 비교자( `Comparator` )를 만들어서 넘겨 주면 된다. 이렇게 직접 구현한 비교자를 전달하면 객체가 기본으로 가지고 있는 `Comparable` 을 무시하고, 별도로 전달한 Comparator를 사용해서 정렬한다.
- 이 때, 전달받은 Comparator가 항상 우선권을 가진다.

## 객체 비교 시 주의할 점

- 만약 Comparable도 구현하지 않고, Comparator도 제공하지 않고, 객체 배열을 정렬하려고 하면 런타임 오류가 발생한다.
- `java.lang.ClassCastException: class collection.compare.MyUser cannot be cast to
  class java.lang.Comparable`
    - 파라미터로 받은 Comparator 없음 → 객체가 갖고 있는 기본 정렬을 사용하려고 함 → Comparable이 없으므로 예외 발생
- Java가 제공하는 Integer, String 같은 기본객체들은 대부분 Comparable을 구현해뒀다.

## Java의 정렬

- 객체의 정렬이 필요한 경우 `Comparable` 을 통해 기본 자연 순서를 제공하자. 자연 순서 외에 다른 정렬 기준이 추가 로 필요하면 `Comparator` 를 제공하자.

## List와 정렬

```java
public static void main(String[] args) {
        MyUser a = new MyUser("a", 30);
        MyUser b = new MyUser("b", 20);
        MyUser c = new MyUser("c", 10);

        LinkedList<MyUser> myUsers = new LinkedList<>(Arrays.asList(a, b, c));

				Collections.sort(list); // 기본정렬 -> 객체의 sort()메서드가 최신이므로 myUsers.sort() 메서드 권장
        myUsers.sort(null); // 객체의 기본 정렬 사용(java 1.8 부터 사용)
        myUsers.sort(new IdComparator()); // 전달받은 Comparator로 비교
    }
```

## Tree와 정렬

- TreeSet, TreeMap 은 Comparable or Comparator 가 필수
- TreeSet과 같은 이진 탐색 트리 구조는 데이터 보관시, 데이터를 정렬하면서 보관 → 비교자(정렬 기준) 무조건 제공되어야 한다.

```java
public static void main(String[] args) {
        MyUser a = new MyUser("a", 30);
        MyUser b = new MyUser("b", 20);
        MyUser c = new MyUser("c", 10);

        MyUser [] myUsers = {a,b,c};

        // MyUser객체의 기본 정렬 사용
        Set<MyUser> treeSet = new TreeSet<>(Arrays.asList(myUsers));
        System.out.println(treeSet);

        // 정렬 기준을 새로 주고 싶다면 객체 생성시에 비교자를 줌
        TreeSet<MyUser> treeSet2 = new TreeSet<>(new IdComparator());
        treeSet2.addAll(Arrays.asList(myUsers));
        System.out.println(treeSet2);
    }
```

- TreeSet 생성시에 별도의 비교자를 제공해주지 않으면 객체가 구현한 Comparable을 사용한다.
- 별도의 비교자를 사용하고 싶다면 TreeSet생성시에 별도로 구현한 비교자를 제공하면 된다
