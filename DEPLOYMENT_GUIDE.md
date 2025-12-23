# 🚀 Streamlit Cloud 배포 가이드

## 배포 준비 완료 ✅

본 프로젝트는 Streamlit Cloud에 배포할 준비가 완료되었습니다.

---

## 📋 배포 전 체크리스트

- [x] frontend/backend 폴더 구조 분리
- [x] requirements.txt 파일 존재
- [x] .streamlit/config.toml 설정 완료
- [x] GitHub 저장소에 푸시 완료
- [x] 환경 변수 설정 (.env.example 제공)

---

## 🌐 GitHub Repository

**URL**: https://github.com/leejaeyoung-cpu/MOVIE

### 주요 브랜치
- `main`: 메인 브랜치 (배포용)

---

## 🎯 Streamlit Cloud 배포 방법

### 1단계: Streamlit Cloud 접속
https://share.streamlit.io/

### 2단계: 새 앱 배포
1. "New app" 클릭
2. Repository 선택: `leejaeyoung-cpu/MOVIE`
3. Branch 선택: `main`
4. Main file path: `frontend/app.py`
5. "Deploy!" 클릭

### 3단계: 환경 변수 설정 (Advanced settings)

필요한 경우 다음 환경 변수 추가:
```
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
```

---

## ⚠️ 중요 사항

### 백엔드 배포

**주의**: Streamlit Cloud는 프론트엔드만 배포합니다!

백엔드를 별도로 배포해야 합니다:

1. **옵션 1: Render.com (무료)**
   - https://render.com
   - Backend 폴더를 Web Service로 배포
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **옵션 2: Railway.app (무료)**
   - https://railway.app
   - Backend 폴더를 배포
   - Procfile 자동 감지

3. **옵션 3: Heroku**
   - Backend 배포 가능
   - Procfile 제공됨

### 환경 변수 업데이트

백엔드를 배포한 후, 프론트엔드의 API URL을 업데이트하세요:

`frontend/utils/api_client.py`:
```python
BASE_URL = "https://your-backend-url.com"  # 백엔드 URL로 변경
```

---

## 📱 로컬 테스트

배포 전 로컬에서 테스트:

```bash
# 백엔드 실행
cd backend
uvicorn app.main:app --reload

# 프론트엔드 실행 (새 터미널)
cd frontend
streamlit run app.py
```

---

## 🔗 예상 배포 URL

### Streamlit Cloud (프론트엔드)
- https://leejaeyoung-cpu-movie.streamlit.app
  (실제 URL은 배포 후 확인)

### Backend 배포 옵션
- Render: https://your-app.onrender.com
- Railway: https://your-app.up.railway.app
- Heroku: https://your-app.herokuapp.com

---

## 💡 배포 팁

### 1. 무료 티어 제한
- Streamlit Cloud: 무료로 1개 private + 무제한 public 앱
- Render: 750시간/월 무료
- Railway: $5 무료 크레딧

### 2. 성능 최적화
- 모델 캐싱 활성화: `@st.cache_resource`
- AI 모델은 경량화 모드 사용
- LLM은 필요시에만 호출

### 3. 데이터베이스
- SQLite는 읽기 전용으로만 사용
- Production은 PostgreSQL 권장 (Railway/Render 무료 제공)

---

## 📊 배포 상태 확인

배포 후 다음 사항을 확인하세요:

### 프론트엔드 체크
- [ ] 메인 페이지 로드
- [ ] 영화 목록 표시
- [ ] 리뷰 작성 기능
- [ ] AI 분석 결과 표시

### 백엔드 체크
- [ ] API Docs 접근 (/docs)
- [ ] Health Check (/health)
- [ ] 영화 API 동작
- [ ] 리뷰 API 동작

---

## 🆘 문제 해결

### 문제 1: 백엔드 연결 실패
**해결**: `frontend/utils/api_client.py`에서 BASE_URL 확인

### 문제 2: 모델 로딩 시간 초과
**해결**: config.py에서 ENABLE_QUANTIZATION = True

### 문제 3: 데이터베이스 오류
**해결**: 초기화 스크립트 실행 또는 샘플 데이터 재생성

---

## 📞 지원

문제가 발생하면:
1. GitHub Issues: https://github.com/leejaeyoung-cpu/MOVIE/issues
2. Streamlit Community: https://discuss.streamlit.io/
3. 로그 확인: Streamlit Cloud 대시보드

---

**작성일**: 2025년 12월 23일  
**상태**: 배포 준비 완료 ✅
