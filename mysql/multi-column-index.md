# 다중 컬럼 인덱스 사용시 주의할 점

```sql
select * from user where col_1 = ? and col_2 = ? and col3 = ? and col4 = ?;
```

해당 where 조건으로 조회하려는 경우 아래와 같이 인덱스를 걸면 조회성능을 향상시킬 수 있다.

```sql
create index user_index
    on user (col_1, col_2, col_3, col_3);
```

그런데 where 절의 조건이 계속 변경되어도 인덱스가 사용될까?

예를 들어 이런 쿼리가 있고, where 절의 조건은 계속 바뀌고,

```sql
select *
from user_group
where 
  and user_id = ?
  and country = ?
  and email = ?;
```

인덱스가 다음처럼 걸려있을 때, 조건의 모든 조합에 인덱스가 사용되는지 테스트해보자.

```sql
create index user_group_user_id_country_email_index
    on user_group (user_id, country, email);
```

조건이 다음과 같이 index 순서대로라면 `user_group_user_id_country_email_index`를 사용한다.

```sql
select *
from user_group
where
  and user_id = 123
  and country = 'KR'
  and email = 'swim@gmail.com';
```

```json
{
    "id": 1,
    "select_type": "SIMPLE",
    "table": "user_group",
    "type": "const",
    "possible_keys": "user_group_user_id_country_email_index",
    ...
  }
```

그러나 다음 조건처럼 인덱스의 세번째 컬럼만 조건으로 사용되었다면, 인덱스를 사용하지 않는다.

```sql
select *
from user_group
where email = 'swim@gmail.com';
```

```json
[
  {
    "id": 1,
    "select_type": "SIMPLE",
    "table": "user_group",
    "type": "const",
    "possible_keys": "",
    ...
  }
]
```

왜냐하면 다중 컬럼 인덱스는 인덱스가 정의된 순서대로 첫 번째 컬럼부터 순차적으로 조건을 만족해야 효과적으로 사용 되기 때문이다.

mysql 에서 다중 컬럼 인덱스는 여러 컬럼을 하나의 인덱스 키로 결합하여 관리한다. 

예를 들어 (column1, column2, column3) 순으로 다중 컬럼 인덱스를 생성하면, 인덱스 키는 첫 번째 컬럼(column1)을 기준으로 정렬되고, 같은 값의 첫 번째 컬럼에 대해 두 번째 컬럼(column2)으로 정렬, 그 다음 세 번째 컬럼(column3)으로 정렬된다.

그리고 인덱스를 사용하여 쿼리를 최적화할 때, 인덱스의 첫 번째 컬럼부터 차례대로 조건을 확인한다. 
첫 번째 컬럼에 조건이 명시되지 않으면, 두 번째 컬럼에 대한 인덱스를 사용할 수 없게 되는데, 
이는 B-Tree 인덱스의 특성상 첫 번째 컬럼의 값이 결정되지 않으면 두 번째, 세 번째 컬럼의 값을 효과적으로 찾을 수 없기 때문이다.
즉, 선행하는 컬럼에 대한 조건이 없는 경우, 작업의 범위를 결정할 '작업 범위 결정 조건(range defining condition)'을 정하지 못해 인덱스를 사용하지 못하게 된다.

예시 인덱스에서는 user_id, country, email 순서대로 최적화된다.
`CREATE INDEX user_group_user_id_country_email_index ON user_group(user_id, country, email);`

따라서, 다중 컬럼 인덱스를 사용하려면 인덱스가 정의된 순서대로 조건을 따라야 한다.