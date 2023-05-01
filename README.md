# mycookie-backend
쪽지메신저웹 🍪내가만든쿠키🍪 백엔드 서버
배포url: https://make.mycookie.site

기술 스택 : React(프론트엔드) + Django(백엔드)

장고 라이브러리 : daphne, channels, rest_framework, corsheaders, django_crontab

주요 구현 사항:

- 실시간 알림 기능 구현(웹 서버 아키텍쳐: gunicorn + daphne + nginx)
: Django chnnels-websocket을 사용한 실시간 쪽지 알림 기능 구현(+ 실시간 읽음 확인 구현) 및 실시간 접속자 확인 기능 구현

- redis + caching 도입을 통한 API 응답 시간 단축

<img width="100%" src="https://ds3h3lok6dodu.cloudfront.net/video/%EB%82%B4%EA%B0%80%EB%A7%8C%EB%93%A0%EC%BF%A0%ED%82%A4_%EC%8B%9C%EC%97%B0%EC%98%81%EC%83%81.gif"/>

웹서버 아키텍처

![image](https://user-images.githubusercontent.com/120891914/235410782-1ee72d41-0721-4a47-945d-9b71d7416c12.png)

데이터베이스 구조

![models](https://user-images.githubusercontent.com/120891914/235413327-f2116af1-edfb-47b2-87f4-c8cb68a440af.png)

