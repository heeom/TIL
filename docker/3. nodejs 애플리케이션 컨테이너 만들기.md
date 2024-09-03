## nodejs 애플리케이션 컨테이너 만들기


### hello.js 작성

```bash
root@e20181cba53f:/# mkdir hellojs
root@e20181cba53f:/# cd hellojs/
root@e20181cba53f:/hellojs# cat > hello.js
```

```bash
const http = require('http');
const os = require('os');
console.log("Test server starting...");

var handler = function(request, response) {
	console.log("Received request from " + request.connection.remoteAddress);
response.writeHead(200);
response.end("host name " + os.hostname());
};

var server = http.createServer(handler);
server.listen(8080);
```

- 8080 포트 listen하는 웹서버
- 8080 포트로 접속하면 클라이언트에게 response로 200, hostname을 내려준다





### Docker File 작성

```bash
vi dockerfile
```

```bash
FROM node:12 # base-image (hello.js를 실행시켜줄 수 있는 운영환경)
COPY hello.js / # 소스를 컨테이너의 최상위 디렉토리에 복사
CMD ["node", "/hello.js"] # 컨테이너가 실행될때 node라는 명령어로 루트에 있는 hello.js를 실행시켜라
```




### 컨테이너 이미지 빌드

```bash
root@e20181cba53f:/hellojs# docker build -t hellojs:latest .
```

- . → 도커 호스트의 작업 디렉토리

- 컨테이너 이미지 생성됨
![image](https://github.com/user-attachments/assets/11f07fc5-4112-4a0b-8f8d-081f2361c1cf)





### 컨테이너 실행

```bash
docker run -d -p 8080:8080 --name node hellojs:latest
```

<img width="914" alt="스크린샷 2024-08-15 오후 9 39 20" src="https://github.com/user-attachments/assets/9780ef66-a3a4-443f-bfec-0581abdf3213">
