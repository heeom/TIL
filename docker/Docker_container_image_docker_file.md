# Docker - container, image, docker file
### Container?

- 컨테이너는 개발한 애플리케이션(실행파일)과 운영환경이 모두 들어있는 독립된 공간
    - 컨테이너는 하나의 Application 프로세스
    - 각 컨테이너는 서로 독립적이다.
- Docker Host?
    - docker 데몬이 동작되고 있는 플랫폼(Linux Kernel)
    - container가 이 위에 올라가고 모든 컨테이너는 동일한 커널을 사용한다.

### container 와 image 차이

- image : 디스크에 레이어별로 저장되어 있는 파일
- Container : 실행중인 프로세스
- 이미지는 read-only, 컨테이너화 되어야 read-write가 가능하다

### Container 실행하기

- Docker Hub : 도커 이미지들이 저장되어있는 공간

```bash
$ docker search nginx # 도커 허브에 nginx가 있는지 검색
$ docker pull niginx:latest # nginx 이미지 다운로드
$ docker run -d --name web -p 80:80 niginx:latest # 컨테이너 실행
```

### DockerFile?

- docker file을 이용해서 컨테이너를 빌드한다 (Container를 만들 수 있도록 도와주는 명령어 집합)
- text-file로 top-down 으로 해석
- 컨테이너 이미지를 생성할 수 있는 instruction을 가짐
- 대소문자 구분하지 않지만 가독성을 위해 구분

### DockerFile 문법

| 명령어 | 설명 |
| --- | --- |
| # | comment |
| FROM | 컨테이너의 base image(운영환경) |
| RUN | 컨테이너 빌드를 위해 base image에서 실행할 commands |
| COPY | 컨테이너를 빌드하는 시점에 호스트의 파일(소스코드)을 컨테이너로 복사 |
| ADD | 컨테이너를 빌드하는 시점에 호스트의 파일(tar, url 포함)을 컨테이너로 복사 |
| WORKDIR | 컨테이너 빌드시 명령이 실행될 작업 디렉터리 설정 |
| ENV | 환경변수 지정 |
| USER | 명령 및 컨테이너 실행시 적용할 유저 설정 |
| EXPOSE | 컨테이너 동작 시 외부에서 사용할 포트 지정 |
| CMD | 컨테이너가 실행될때 자동으로 실행할 서비스나 스크립트 |
