# MLOps 텍스트 감정 분석 프로젝트 (CI/CD Pipeline)

이 프로젝트는 간단한 텍스트 감정 분석(Sentiment Analysis)을 수행하는 AI 애플리케이션으로, **GitHub Actions**와 **Docker Hub**, **Self-hosted Runner**를 이용하여 전체적인 MLOps CI/CD 파이프라인을 구축한 결과물입니다.

---

## 1. 프로젝트 구조

```text
MLOps_HW2/
│ 
├─ .github/
│  └─ workflows/
│     └─ main.yml          # GitHub Actions CI/CD 파이프라인 스크립트
│ 
├─ templates/
│  └─ index.html           # 프론트엔드 UI 화면
│ 
├─ .dockerignore           # Docker 빌드 시 무시할 목록
├─ .gitignore              # Git에 올라가지 않을 파일 목록
├─ app.py                  # Flask 웹 API 서버
├─ base_data.csv           # 초기 모델 학습용 데이터셋
├─ feedback_data.csv       # 사용자가 추가한 피드백 데이터
├─ Dockerfile              # 컨테이너화를 위한 도커파일
├─ requirements.txt        # 파이썬 패키지 의존성 파일
├─ retrain.py              # 피드백 데이터를 이용한 재학습 스크립트
└─ train.py                # 모델을 최초에 생성/학습하는 스크립트
```

## 2. 로컬 실행 방법 (Without Docker)

만약 Docker를 사용하지 않고 로컬 환경에서 직접 실행하려면 다음을 따르세요.

1. **가상환경 설정 및 패키지 설치**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
   pip install -r requirements.txt
   ```
2. **초기 모델 학습**
   ```bash
   python train.py
   ```
3. **서버 실행**
   ```bash
   python app.py
   ```
   브라우저에서 `http://127.0.0.1:5000` 으로 접속하여 확인합니다.

---

## 3. Docker 수동 Build/Run 방법

도커가 설치된 터미널에서 다음 명령어로 수동 조작이 가능합니다.

- **도커 이미지 빌드**
  ```bash
  docker build -t mlops-sentiment-app .
  ```
- **도커 컨테이너 실행**
  ```bash
  docker run -d --name mlops-sentiment-app -p 5000:5000 mlops-sentiment-app
  ```
- **실행 확인 후 중지 및 삭제**
  ```bash
  docker stop mlops-sentiment-app
  docker rm mlops-sentiment-app
  ```

---

## 4. GitHub Secrets 설정 방법

GitHub Actions가 자동으로 내 Docker Hub에 이미지를 Push하게 하려면 권한 정보가 필요합니다.
1. GitHub 레포지토리의 상단 **Settings**로 이동합니다.
2. 좌측 메뉴의 **Secrets and variables** > **Actions** 메뉴를 클릭합니다.
3. **[New repository secret]** 버튼을 눌러 다음 두 값을 등록합니다.
   - `DOCKERHUB_USERNAME` : 본인의 Docker Hub ID
   - `DOCKERHUB_TOKEN` : Docker Hub에서 발급한 Access Token (비밀번호도 가능하지만, Access Token을 권장)

---

## 5. Self-hosted Runner 등록 방법

로컬 컴퓨터(내 PC)를 CD 배포 대상으로 만들기 위한 과정입니다.
1. GitHub 레포지토리의 상단 **Settings**로 이동합니다.
2. 좌측 메뉴의 **Actions** > **Runners** 메뉴를 클릭합니다.
3. **[New self-hosted runner]** 버튼을 클릭합니다.
4. 본인의 운영체제(Mac/Windows/Linux)와 아키텍처에 맞는 것을 선택하면 하단에 긴 터미널 명령어가 나타납니다.
5. 로컬 터미널을 열고 해당 명령어들을 순서대로 붙여넣기 하여 Runner를 설치 및 설정합니다.
6. 마지막으로 `./run.sh` (또는 `run.cmd`) 를 실행하면, 내 터미널이 `Listening for Jobs` 상태가 되면서 파이프라인의 배포 명령을 받아 수행할 준비가 끝납니다.

---

## 6. 전체 CI/CD 동작 흐름

본 시스템의 MLOps 배포 파이프라인 흐름은 다음과 같습니다.
1. **[사용자]** 코드를 수정(UI 변경 혹은 학습 로직 수정)한 뒤 `git commit` 후 `git push`를 진행합니다.
2. **[GitHub Actions CI 단계]** 즉시 클라우드 서버가 동작하여, 프로젝트를 최신 Docker 이미지 상태로 Build하고, Docker Hub에 `YOUR_USERNAME/mlops-sentiment-app:latest` 태그로 Push 합니다.
3. **[GitHub Actions CD 단계]** 빌드가 성공하면, 미리 연결된 **내 로컬 PC(Self-hosted Runner) 화면**으로 명령이 하달되어 기존 컨테이너를 삭제하고, 최신 이미지를 다운 받아 포트 5000번으로 재가동합니다.

---

## 7. 트러블슈팅 및 로그 확인 위치 (Log Points)

파이프라인이나 서비스가 실패했을 경우 다음의 단계를 역추적하세요.
1. **GitHub Actions Build 단계 (`build-and-push`)**: 패키지 충돌이나 문법 오류가 있었다면 깃헙 웹페이지 Actions 탭 내 Build 단계에서 붉은 에러 마크가 뜸.
2. **Docker Hub Login 단계**: Secrets 오타나 권한 문제가 있다면 Login-action 부분에서 `Authentication failed` 관련 에러가 발생.
3. **Self-hosted Runner Deploy 단계**: 로컬에 Runner 터미널 창(ex: `./run.sh`)이 꺼져 있다면 Offline 상태로 대기하다가 Fail 처리됨.
4. **Container Startup 로그**: 컨테이너가 켜졌지만 웹에 접속이 안 될 땐, 로컬 터미널에서 아래 명령어로 문제가 있는지 확인.
   ```bash
   docker logs mlops-sentiment-app
   ```

---

## 8. MLOps (모델/로직 업데이트) 동작 검증 방법

파이프라인 구축이 성공적이면, 다음 시나리오로 "수정 -> Push -> 자동 재배포 완료" 여부를 테스트하세요.

1. `app.py` 의 `/predict` API 에서 반환하는 결과 포맷의 이름을 살짝 수정해 봅니다. (예: `"prediction": ...` 부분을 `"AI_prediction": ...` 으로 변경)
2. 변경 사항을 Push 합니다. (`git add app.py`, `git commit -m "Update API response"`, `git push origin main`)
3. GitHub 레포지토리의 **Actions 탭**에 들어가서 초록색 노드가 CI -> CD 순으로 체크(`✔`) 되는지 약 1~2분 정도 구경합니다.
4. 완료 즉시, 브라우저에서 `http://localhost:5000` 접속이 제대로 되는지, 혹은 UI 상에서 글을 입력했을 때 분석 결과가 방금 바꾼 코드대로 (`AI_prediction` 형태로) 정상 표출되는지 확인합니다. 이것이 완벽하게 이루어졌다면 **자동 대응형 MLOps 파이프라인 구축 성공**입니다.
