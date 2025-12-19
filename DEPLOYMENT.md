# 🚀 배포 가이드

이 가이드는 영화 리뷰 AI 시스템을 프로덕션 환경에 배포하는 방법을 설명합니다.

---

## 📋 배포 전 체크리스트

- [ ] 모든 환경 변수가 `.env.example`에 문서화되어 있는지 확인
- [ ] API 키가 코드에 하드코딩되지 않았는지 확인
- [ ] 데이터베이스가 정상 작동하는지 확인
- [ ] 모든 dependencies가 `requirements.txt`에 있는지 확인

---

## 🎯 배포 옵션

### 옵션 1: Streamlit Cloud (권장 - 프론트엔드)

**장점:**
- ✅ 무료
- ✅ 간단한 설정
- ✅ GitHub 연동

**단계:**

1. **Streamlit Cloud에 가입**
   ```
   https://streamlit.io/cloud
   ```

2. **New app 생성**
   - Repository: `your-username/MOVIE`
   - Branch: `main`
   - Main file path: `frontend/app.py`

3. **환경 변수 설정**
   ```
   OMDB_API_KEY=your_key_here
   ```

4. **Advanced settings**
   ```
   Python version: 3.11
   ```

5. **Deploy!**

---

### 옵션 2: Railway (권장 - 백엔드)

**장점:**
- ✅ 프론트엔드 + 백엔드 모두 배포 가능
- ✅ 자동 HTTPS
- ✅ 무료 티어 제공

**단계:**

1. **Railway 가입**
   ```
   https://railway.app
   ```

2. **New Project → Deploy from GitHub repo**
   - Repository 선택

3. **환경 변수 설정**
   ```env
   OMDB_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   DATABASE_URL=postgresql://... (Railway가 자동 생성)
   SECRET_KEY=your_secret_key
   ```

4. **백엔드 서비스 설정**
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **프론트엔드 서비스 설정** (선택사항)
   - Start Command: `cd frontend && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

---

### 옵션 3: Render

**장점:**
- ✅ 무료 PostgreSQL
- ✅ 간단한 설정
- ✅ 자동 배포

**단계:**

1. **Render 가입**
   ```
   https://render.com
   ```

2. **New Web Service**
   - Repository 연결
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **환경 변수 설정**
   ```
   OMDB_API_KEY=...
   OPENAI_API_KEY=...
   DATABASE_URL=...
   ```

---

## 🔧 데이터베이스 설정

### 로컬 개발 (SQLite)
```env
DATABASE_URL=sqlite:///./movie_reviews.db
```

### 프로덕션 (PostgreSQL)
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**마이그레이션:**
```bash
# SQLite → PostgreSQL 마이그레이션
python migrate_db.py
```

---

## 🌐 환경 변수 설정

모든 배포 플랫폼에서 다음 환경 변수를 설정해야 합니다:

### 필수 환경 변수

```env
# OMDb API (영화 정보)
OMDB_API_KEY=your_omdb_api_key

# OpenAI API (LLM 기능)
OPENAI_API_KEY=sk-proj-your_key_here

# 데이터베이스
DATABASE_URL=sqlite:///./movie_reviews.db  # 로컬
DATABASE_URL=postgresql://...              # 프로덕션

# 보안
SECRET_KEY=your_very_secret_random_string_here
```

### 선택적 환경 변수

```env
# 디버그 모드 (프로덕션에서는 false)
DEBUG=false

# CORS 설정
CORS_ORIGINS=https://your-frontend-domain.com
```

---

## 📦 Docker 배포 (선택사항)

Docker를 사용하여 배포할 수도 있습니다:

### 1. Dockerfile 생성

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 백엔드 실행
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/movie
      - OMDB_API_KEY=${OMDB_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

---

## 🔍 배포 후 확인

배포가 완료되면 다음을 확인하세요:

1. **백엔드 API 확인**
   ```
   https://your-backend-url.com/docs
   ```

2. **프론트엔드 확인**
   ```
   https://your-frontend-url.com
   ```

3. **API 연결 테스트**
   - 영화 목록 페이지 접속
   - 영화 추가 기능 테스트
   - 시스템 설정 확인

4. **로그 확인**
   - 에러 로그 확인
   - API 요청 로그 확인

---

## ⚠️ 프로덕션 주의사항

### 보안

1. **API 키 보호**
   - 절대 코드에 하드코딩 금지
   - 환경 변수 사용
   - .env 파일은 .gitignore에 추가

2. **SECRET_KEY 변경**
   ```python
   # 강력한 랜덤 키 생성
   import secrets
   print(secrets.token_urlsafe(32))
   ```

3. **CORS 설정**
   - 프로덕션 도메인만 허용
   - `CORS_ORIGINS`에 실제 도메인 설정

### 성능

1. **데이터베이스**
   - SQLite → PostgreSQL 마이그레이션
   - 인덱스 최적화
   - 연결 풀링 설정

2. **캐싱**
   - Redis 추가 고려
   - API 응답 캐싱

3. **스케일링**
   - 워커 수 증가
   - 로드 밸런서 추가

---

## 📊 모니터링

### 로그 수집

```python
# backend/app/main.py에 추가
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 에러 추적

- Sentry 통합
- New Relic
- Datadog

---

## 🆘 트러블슈팅

### 일반적인 문제

**1. 데이터베이스 연결 실패**
```
해결: DATABASE_URL 환경 변수 확인
```

**2. API 키 오류**
```
해결: OMDB_API_KEY, OPENAI_API_KEY 확인
```

**3. CORS 에러**
```
해결: backend/app/config.py의 CORS_ORIGINS 설정
```

**4. 포트 충돌**
```
해결: PORT 환경 변수 설정
```

---

## 🔄 CI/CD 설정 (선택사항)

GitHub Actions를 사용한 자동 배포:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## ✅ 배포 체크리스트

배포 전:
- [ ] 환경 변수 모두 설정됨
- [ ] API 키 작동 확인
- [ ] 데이터베이스 마이그레이션 완료
- [ ] SECRET_KEY 변경됨
- [ ] CORS 설정 완료

배포 후:
- [ ] 백엔드 API 작동 확인
- [ ] 프론트엔드 로딩 확인
- [ ] 영화 목록 표시 확인
- [ ] 영화 추가 기능 확인
- [ ] 로그 확인

---

## 📚 추가 리소스

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-cloud)
- [Railway 문서](https://docs.railway.app/)
- [Render 문서](https://render.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)

---

**🎉 배포 완료를 축하합니다!**

문제가 발생하면 GitHub Issues에 등록하세요.
