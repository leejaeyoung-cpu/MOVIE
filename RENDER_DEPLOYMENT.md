# Render.com 배포 가이드

## 🚀 빠른 배포

### 1. Render.com 회원가입
https://render.com/

### 2. New Web Service 생성

#### Repository 연결
- **GitHub Repository**: `leejaeyoung-cpu/MOVIE`
- **Branch**: `main`

#### 설정
- **Name**: `movie-backend` (원하는 이름)
- **Region**: `Singapore` (한국과 가장 가까움)
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements-cloud.txt
  ```
- **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### 요금제
- **Free** 선택

### 3. 환경 변수 설정

**Environment Variables** 섹션에서 추가:

| Key | Value | 설명 |
|-----|-------|------|
| `OPENAI_API_KEY` | `your-key` | (선택) LLM 사용 시 |
| `ANTHROPIC_API_KEY` | `your-key` | (선택) Claude 사용 시 |
| `DEBUG` | `False` | Production 모드 |

### 4. 배포하기

**Create Web Service** 버튼 클릭!

배포 완료까지 약 5-10분 소요됩니다.

---

## 🔗 배포 완료 후

### 백엔드 URL 확인
Render가 제공하는 URL (예: `https://movie-backend-abc123.onrender.com`)

### 프론트엔드 연결

`frontend/utils/api_client.py` 수정:

```python
# 배포된 백엔드 URL로 변경
API_URL = "https://movie-backend-abc123.onrender.com"
```

변경 후 GitHub에 푸시하면 Streamlit Cloud가 자동으로 업데이트됩니다!

---

## ⚠️ 무료 티어 제한사항

### Render.com Free Tier
- ✅ 무료로 사용 가능
- ⚠️ 15분 동안 요청 없으면 sleep
- ⚠️ 첫 요청 시 cold start (30초~1분)
- ✅ 750시간/월 사용 가능

### 해결방법
1. **Keep-alive 서비스** 사용
   - UptimeRobot (https://uptimerobot.com/)
   - 5분마다 health check 요청

2. **유료 전환** ($7/월)
   - Sleep 없음
   - 빠른 응답

---

## 🎯 현재 배포된 requirements-cloud.txt

경량화된 버전:
- ✅ FastAPI, SQLAlchemy (핵심 기능)
- ✅ OpenAI, Anthropic (LLM API만)
- ❌ PyTorch, Transformers (로컬 AI 제외)
- ❌ GNN, RL 등 무거운 패키지 제외

### AI 기능 제한
클라우드 배포 시:
- ❌ Multi-Model Ensemble (로컬만)
- ❌ Aspect-Based SA (로컬만)
- ✅ LLM 요약 (API 사용)
- ✅ 기본 CRUD (정상 작동)

**완전한 AI 기능은 로컬 실행 시에만 사용 가능합니다!**

---

## 💡 추천 구성

### 옵션 1: 하이브리드 (권장)
- **프론트엔드**: Streamlit Cloud (무료)
- **백엔드**: 로컬 실행 (완전한 AI 기능)
- **데모**: UI만 클라우드에서 확인

### 옵션 2: 풀 클라우드
- **프론트엔드**: Streamlit Cloud
- **백엔드**: Render.com (기본 CRUD만)
- **AI**: LLM API만 사용

### 옵션 3: 로컬 전용
- **모든 기능**: 로컬에서 실행
- **장점**: 완전한 AI 기능
- **단점**: 항상 실행 필요

---

## 📞 문제 해결

### 빌드 실패 시
1. `requirements-cloud.txt` 확인
2. Python 버전 확인 (3.11 권장)
3. Render 로그 확인

### 시작 실패 시
1. 환경 변수 확인
2. Start Command 확인
3. Port가 `$PORT`인지 확인

---

**작성일**: 2025-12-23  
**Render Docs**: https://render.com/docs
