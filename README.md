# 🎬 영화 리뷰 AI 시스템

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://leemove.streamlit.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

## 🌐 데모

**Live Demo (프론트엔드 UI)**: https://leemove.streamlit.app/

> ⚠️ **알림**: 현재 데모는 UI/UX 프리뷰용입니다. 백엔드 API가 연결되지 않아 실제 AI 분석 기능은 로컬 실행시에만 동작합니다.

## 🚀 빠른 시작 (로컬 실행 - 전체 기능)

### 1. Clone Repository
```bash
git clone https://github.com/leejaeyoung-cpu/MOVIE.git
cd MOVIE
```

### 2. 백엔드 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

접속: http://localhost:8000  
API Docs: http://localhost:8000/docs

### 3. 프론트엔드 실행 (새 터미널)
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

접속: http://localhost:8501

## ✨ 주요 기능

### 프론트엔드 (Streamlit)
- 🎬 **영화 목록** - 제목, 포스터, 평균 평점 표시
- ➕ **영화 추가** - 제목, 개봉일, 감독, 장르, 포스터 URL 입력
- ✍️ **리뷰 작성** - AI 자동 감성 분석
- 📊 **분석 대시보드** - 리뷰 통계 및 시각화
- 🎯 **AI 추천** - 개인화 영화 추천

### 백엔드 (FastAPI)
- 🎭 **영화 관리 API** - CRUD 기능
- 💬 **리뷰 관리 API** - 작성, 조회, 삭제
- 🤖 **AI 감성 분석**
  - Multi-Model Ensemble (KoBERT + RoBERTa + ELECTRA)
  - Aspect-Based Sentiment Analysis (6개 측면)
  - Multi-Emotion Classification (6가지 감정)
- 🧠 **LLM 통합** - GPT-4/Claude 자동 요약
- 📈 **GNN 추천 시스템** - Graph Neural Network
- ⚡ **성능 최적화** - INT8 양자화, GPU 가속

## 📁 프로젝트 구조

```
MOVIE/
├── frontend/                # Streamlit 프론트엔드
│   ├── app.py               # 메인 앱
│   ├── pages/               # 페이지들
│   ├── utils/               # 유틸리티
│   └── requirements.txt
│
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py          # FastAPI 앱
│   │   ├── models/          # DB 모델
│   │   ├── routers/         # API 라우터
│   │   └── services/        # AI 서비스
│   └── requirements.txt
│
└── README.md
```

## 🔧 기술 스택

### Frontend
- **Streamlit** - 웹 UI 프레임워크
- **Plotly** - 인터랙티브 차트
- **Requests** - API 통신

### Backend
- **FastAPI** - 고성능 웹 프레임워크
- **SQLAlchemy** - ORM
- **SQLite** - 데이터베이스
- **Transformers** - AI 모델 (KoBERT, RoBERTa, ELECTRA)
- **PyTorch** - 딥러닝 프레임워크
- **OpenAI / Anthropic** - LLM API

## 📊 데이터베이스 (ERD)

### 핵심 테이블
- **movies** - 영화 정보 (제목, 감독, 장르, 포스터)
- **reviews** - 리뷰 및 감성 분석 결과
- **ratings** - 영화별 평점 통계

### 관계
- `movies` ↔ `reviews`: 1:N
- `movies` ↔ `ratings`: 1:1

## 🎯 API 엔드포인트

### 영화
- `POST /api/movies/` - 영화 등록
- `GET /api/movies/` - 영화 목록
- `GET /api/movies/{id}` - 특정 영화
- `DELETE /api/movies/{id}` - 영화 삭제

### 리뷰
- `POST /api/reviews/` - 리뷰 작성 + AI 분석
- `GET /api/reviews/` - 리뷰 목록
- `GET /api/reviews/movie/{id}` - 특정 영화 리뷰
- `DELETE /api/reviews/{id}` - 리뷰 삭제

### 추천
- `POST /api/recommendations/` - 개인화 추천
- `GET /api/recommendations/similar/{id}` - 유사 영화
- `GET /api/recommendations/trending` - 인기 영화

## 🌟 특별 기능

### AI 감성 분석
- **Multi-Model Ensemble**: 3개 모델 앙상블 → 95%+ 정확도
- **Aspect-Based SA**: 연기, 스토리, 영상미, 음악, 연출, 각본
- **Multi-Emotion**: 기쁨, 슬픔, 분노, 놀람, 공포, 혐오

### 추천 시스템
- **GNN (Graph Neural Networks)**: 영화-배우-감독-장르 그래프
- **Reinforcement Learning**: 사용자 피드백 학습
- **개인화**: 사용자별 맞춤 추천

### 성능 최적화
- **INT8 양자화**: 4배 빠른 추론
- **GPU 가속**: CUDA 지원
- **모델 캐싱**: 메모리 최적화

## 🚀 배포

### Streamlit Cloud (프론트엔드)
현재 배포됨: https://leemove.streamlit.app/

### 백엔드 배포 옵션
1. **Render.com** (권장)
2. **Railway.app**
3. **Heroku**

자세한 내용은 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 참고

## 📚 문서

- [제출완료.md](제출완료.md) - 프로젝트 제출 요약
- [MISSION_COMPLIANCE_REPORT.md](MISSION_COMPLIANCE_REPORT.md) - 요구사항 분석
- [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md) - 성능 평가
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 배포 가이드
- [스프린트미션18_보고서.pdf](스프린트미션18_보고서.pdf) - 공식 보고서

## 📄 라이선스

MIT License

## 👨‍💻 개발자

- GitHub: [@leejaeyoung-cpu](https://github.com/leejaeyoung-cpu)
- Repository: [MOVIE](https://github.com/leejaeyoung-cpu/MOVIE)

## 🙏 감사의 말

본 프로젝트는 스프린트 미션 18의 일환으로 개발되었습니다.

---

**Made with ❤️ using FastAPI + Streamlit + AI**
