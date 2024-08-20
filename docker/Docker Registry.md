## 컨테이너 Registry

- Registry : 컨테이너 이미지를 저장하고 관리하는 저장소
- Docker hub : Docker에서 제공하는 public Registry 서비스
    - [hub.docker.com](http://hub.docker.com)
    - docker hub에서 이미지 검색 및 다운로드
        - `docker search mysql`
        - `docker pull httpd:latest`
- private Registry : 사내 컨테이너 저장소

## Private Registry

- registry 컨테이너를 이용해서 private 컨테이너 운영할 수 있다.
- private registry에 업로드하는 이미지 명은 호스트네임과 포트명이 필수
    - docker.example.com:5000/ubuntu:18.04

## Public 저장소 사용하기

### 도커 hub 로그인하기

```bash
docker login
```

### 태그 붙이기

```bash
docker tag hello-world:latest heeom/hello-world:latest
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/72038517-8ad4-4bad-a50e-fa0deed31c0b/669ab9d9-f89d-4702-9bb3-c878149f5291/image.png)

### public 저장소에 push

```bash
docker push heeom/hello-world:latest
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/72038517-8ad4-4bad-a50e-fa0deed31c0b/69542986-dbfc-4598-b54e-4e4436226530/image.png)

## Docker Registry를 사용해서 Private Registry 구축하기

[registry - Official Image | Docker Hub](https://hub.docker.com/_/registry)

### Docker Registry 시작

```bash
$ docker run -d -p 5001:5000 --restart always --name registry registry:2
```

### Container image tag 붙이기

```bash
docker tag hello-world:latest localhost:5001/hello-world:latest
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/72038517-8ad4-4bad-a50e-fa0deed31c0b/833f32ea-88c3-4ab4-8f17-2ac5317531f5/image.png)

### Private registry에 image 푸시하기

```bash
docker push localhost:5001/hello-world:latest
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/72038517-8ad4-4bad-a50e-fa0deed31c0b/bdb19bc2-1421-416d-b1b9-13233d392f19/image.png)

### Private Registry의 image 접근

- API로 조회

```bash
curl http://localhost:5001/v2/_catalog
```

- Docker CLI로 레지스트리에 접속하여 조회

```bash
docker login localhost:5001
# 이미지 다운로드
docker pull localhost:5001/<image_name>:<tag>
docker images
```
