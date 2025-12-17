"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from .config import settings, print_config
from .database import init_db

# Routers (추후 생성)
# from .routers import movies, reviews, ratings, recommendations

# 라우터 import
from .routers import movies, reviews, recommendations

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Netflix급 영화 리뷰 및 AI 추천 시스템",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("\n" + "=" * 70)
    print(f"🎬 {settings.APP_NAME} v{settings.VERSION}")
    print("=" * 70)
    
    # 설정 출력
    print_config()
    
    # 데이터베이스 초기화
    init_db()
    
    # AI 모델 로딩 (lazy loading - 첫 요청 시)
    print("\n✅ Application started successfully!")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시"""
    print("\n👋 Shutting down...")


# Middleware: 요청 시간 측정
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "features": {
            "gpu": settings.ENABLE_GPU,
            "quantization": settings.ENABLE_QUANTIZATION,
            "gnn": settings.ENABLE_GNN,
            "rl": settings.ENABLE_RL,
            "llm": settings.ENABLE_LLM,
            "absa": settings.ENABLE_ABSA,
            "emotion": settings.ENABLE_EMOTION_CLASSIFICATION
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/config")
async def get_config():
    """현재 설정 조회"""
    from .config import get_model_config
    return get_model_config()


# 라우터 등록
app.include_router(movies.router, prefix="/api/movies", tags=["Movies"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
