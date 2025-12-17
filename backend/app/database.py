"""
데이터베이스 연결 및 세션 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()


# 의존성: DB 세션 가져오기
def get_db():
    """
    FastAPI 의존성으로 사용할 DB 세션
    
    사용 예시:
    ```python
    @app.get("/movies")
    def get_movies(db: Session = Depends(get_db)):
        return db.query(Movie).all()
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 데이터베이스 초기화
def init_db():
    """
    애플리케이션 시작 시 테이블 생성
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
