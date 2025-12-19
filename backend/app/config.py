"""
설정 파일 - 모든 AI/ML 기능 토글 관리
"""

from pydantic_settings import BaseSettings
from typing import Literal
import os

class Settings(BaseSettings):
    """
    애플리케이션 설정
    
    모든 고급 기능을 토글로 on/off 가능
    """
    
    # ===== 기본 설정 =====
    APP_NAME: str = "Movie Review AI System"
    VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # ===== 데이터베이스 =====
    DATABASE_URL: str = "sqlite:///./movie_reviews.db"
    # 프로덕션: "postgresql://user:pass@localhost:5432/moviedb"
    
    # ===== Redis 캐싱 =====
    REDIS_URL: str | None = None  # "redis://localhost:6379"
    ENABLE_REDIS: bool = False
    CACHE_TTL: int = 1800  # 30분
    
    # ===== 보안 =====
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ===== CORS =====
    CORS_ORIGINS: list = ["http://localhost:8501", "http://localhost:3000"]
    
    # ===== OMDb API (Open Movie Database) =====
    OMDB_API_KEY: str | None = None  # OMDb API 키 (환경 변수에서 설정)
    OMDB_BASE_URL: str = "http://www.omdbapi.com"
    ENABLE_OMDB: bool = True  # OMDb API 사용 여부


    
    # ==========================================
    # AI/ML 기능 토글 (핵심!)
    # ==========================================
    
    # ----- GPU/CPU 설정 -----
    ENABLE_GPU: bool = True  # GPU 사용 (False: CPU만 사용)
    GPU_DEVICE: int = 0  # GPU 디바이스 번호
    
    # ----- 모델 경량화 -----
    ENABLE_QUANTIZATION: bool = True  # INT8 양자화 (4배 빠름)
    QUANTIZATION_DTYPE: Literal["int8", "fp16", "fp32"] = "int8"
    QUANTIZATION_BACKEND: Literal["fbgemm", "qnnpack"] = "fbgemm"  # CPU: fbgemm, Mobile: qnnpack
    
    # ----- 감성 분석 모델 -----
    SENTIMENT_MODEL: Literal["kobert", "roberta", "electra", "ensemble"] = "ensemble"
    ENABLE_KNOWLEDGE_DISTILLATION: bool = True  # Teacher → Student
    ENABLE_UNCERTAINTY_ESTIMATION: bool = True  # Monte Carlo Dropout
    
    # ----- Aspect-Based Sentiment Analysis -----
    ENABLE_ABSA: bool = True  # Aspect-Based 감성 분석
    ABSA_ASPECTS: list = ["acting", "plot", "cinematography", "soundtrack", "direction", "screenplay"]
    
    # ----- Multi-Emotion Classification -----
    ENABLE_EMOTION_CLASSIFICATION: bool = True
    EMOTION_LABELS: list = ["joy", "sadness", "anger", "surprise", "fear", "disgust"]
    
    # ----- LLM Integration (비용 발생!) -----
    ENABLE_LLM: bool = False  # ⚠️ API 비용 발생
    LLM_PROVIDER: Literal["openai", "anthropic"] = "openai"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4-turbo-preview"  # or "claude-3-opus-20240229"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    USE_LLM_CACHE: bool = True  # LLM 응답 캐싱
    
    # ----- Contrastive Learning -----
    ENABLE_CONTRASTIVE_LEARNING: bool = True  # SimCSE
    
    # ----- Explainable AI -----
    ENABLE_XAI: bool = True  # LIME, SHAP
    XAI_METHOD: Literal["lime", "shap", "both"] = "both"
    
    # ==========================================
    # 추천 시스템 설정
    # ==========================================
    
    RECOMMENDATION_MODEL: Literal["ncf", "svd", "gnn", "rl", "hybrid"] = "hybrid"
    
    # ----- Neural Collaborative Filtering -----
    ENABLE_NCF: bool = True
    NCF_EMBEDDING_DIM: int = 128
    NCF_LAYERS: list = [256, 128, 64, 32]
    
    # ----- Graph Neural Networks -----
    ENABLE_GNN: bool = True  # ✅ GNN 활성화
    GNN_TYPE: Literal["graphsage", "gat", "gcn"] = "graphsage"
    GNN_HIDDEN_DIM: int = 128
    GNN_NUM_LAYERS: int = 3
    
    # ----- Sequential Recommendation -----
    ENABLE_SEQUENTIAL: bool = True
    SEQUENTIAL_MODEL: Literal["gru", "lstm", "transformer"] = "transformer"
    SEQUENCE_LENGTH: int = 50
    
    # ----- Reinforcement Learning -----
    ENABLE_RL: bool = True  # ✅ RL 활성화
    RL_ALGORITHM: Literal["contextual_bandit", "dqn", "ppo"] = "contextual_bandit"
    RL_EPSILON: float = 0.1  # Exploration rate
    RL_LEARNING_RATE: float = 0.001
    
    # ----- Multi-Task Learning -----
    ENABLE_MULTI_TASK: bool = True
    MTL_TASKS: list = ["rating", "click", "watch_time"]
    MTL_LOSS_WEIGHTS: dict = {"rating": 0.5, "click": 0.3, "watch_time": 0.2}
    
    # ==========================================
    # 성능 최적화
    # ==========================================
    
    # ----- 배치 처리 -----
    ENABLE_DYNAMIC_BATCHING: bool = True
    MAX_BATCH_SIZE: int = 32
    BATCH_TIMEOUT_MS: int = 100  # 100ms 내 요청 묶음
    
    # ----- 비동기 처리 -----
    ENABLE_ASYNC: bool = True
    WORKER_THREADS: int = 4
    
    # ----- ONNX Runtime -----
    ENABLE_ONNX: bool = True  # 2-3배 빠름
    ONNX_OPTIMIZATION_LEVEL: Literal["all", "basic", "extended"] = "all"
    
    # ----- Feature Store -----
    ENABLE_FEATURE_STORE: bool = False
    ONLINE_STORE_TYPE: Literal["redis", "dynamodb"] = "redis"
    OFFLINE_STORE_TYPE: Literal["parquet", "delta"] = "parquet"
    
    # ==========================================
    # 고급 ML 기법
    # ==========================================
    
    # ----- Active Learning -----
    ENABLE_ACTIVE_LEARNING: bool = True
    AL_STRATEGY: Literal["uncertainty", "query_by_committee"] = "uncertainty"
    AL_SAMPLE_SIZE: int = 100
    
    # ----- Data Augmentation -----
    ENABLE_DATA_AUGMENTATION: bool = True
    AUGMENTATION_METHODS: list = ["back_translation", "synonym_replacement", "mixup"]
    
    # ----- Semi-Supervised Learning -----
    ENABLE_SEMI_SUPERVISED: bool = True
    SSL_METHOD: Literal["pseudo_labeling", "mixmatch", "consistency"] = "pseudo_labeling"
    
    # ----- Transfer Learning -----
    ENABLE_TRANSFER_LEARNING: bool = True
    PRETRAINED_MODEL: str = "monologg/kobert"
    
    # ==========================================
    # MLOps
    # ==========================================
    
    # ----- Model Versioning -----
    ENABLE_MLFLOW: bool = False
    MLFLOW_TRACKING_URI: str | None = None
    
    # ----- A/B Testing -----
    ENABLE_AB_TESTING: bool = True
    AB_TEST_SPLIT: float = 0.5  # 50/50 split
    
    # ----- Monitoring -----
    ENABLE_MONITORING: bool = True
    SENTRY_DSN: str | None = None
    PROMETHEUS_PORT: int = 9090
    
    # ----- Drift Detection -----
    ENABLE_DRIFT_DETECTION: bool = True
    DRIFT_THRESHOLD: float = 0.05
    
    # ==========================================
    # 모델 파일 경로
    # ==========================================
    
    MODEL_DIR: str = "./models"
    SENTIMENT_MODEL_PATH: str = f"{MODEL_DIR}/sentiment"
    RECOMMENDATION_MODEL_PATH: str = f"{MODEL_DIR}/recommendation"
    GNN_MODEL_PATH: str = f"{MODEL_DIR}/gnn"
    RL_MODEL_PATH: str = f"{MODEL_DIR}/rl"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 싱글톤 인스턴스
settings = Settings()

# Device selection moved to sentiment_analyzer.py
# def get_device():
#     """
#     사용할 디바이스 반환 (GPU/CPU)
#     """
#     if settings.ENABLE_GPU:
#         import torch
#         if torch.cuda.is_available():
#             return f"cuda:{settings.GPU_DEVICE}"
#         else:
#             print("⚠️  GPU가 활성화되어 있지만 CUDA를 사용할 수 없습니다. CPU를 사용합니다.")
#             return "cpu"
#     return "cpu"


def get_model_config():
    """
    현재 활성화된 모델 설정 요약
    """
    device = "cpu"  # Default device
    if settings.ENABLE_GPU:
        device = f"cuda:{settings.GPU_DEVICE}"
    
    config = {
        "device": device,
        "quantization": settings.ENABLE_QUANTIZATION,
        "sentiment_model": settings.SENTIMENT_MODEL,
        "recommendation_model": settings.RECOMMENDATION_MODEL,
        "enabled_features": {
            "ABSA": settings.ENABLE_ABSA,
            "Emotion": settings.ENABLE_EMOTION_CLASSIFICATION,
            "GNN": settings.ENABLE_GNN,
            "RL": settings.ENABLE_RL,
            "LLM": settings.ENABLE_LLM,
            "XAI": settings.ENABLE_XAI,
        }
    }
    return config


def print_config():
    """
    현재 설정 출력 (디버깅용)
    """
    print("=" * 60)
    print("🎬 Movie Review AI System Configuration")
    print("=" * 60)
    
    config = get_model_config()
    
    print(f"\n🖥️  Device: {config['device']}")
    print(f"⚡ Quantization: {'ON' if config['quantization'] else 'OFF'}")
    print(f"🧠 Sentiment Model: {config['sentiment_model']}")
    print(f"🎯 Recommendation Model: {config['recommendation_model']}")
    
    print("\n✨ Enabled Features:")
    for feature, enabled in config['enabled_features'].items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
    
    print("\n" + "=" * 60)


# 앱 시작 시 설정 출력
if __name__ == "__main__":
    print_config()
