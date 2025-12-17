"""
SQLAlchemy 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Movie(Base):
    """영화 모델"""
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    release_date = Column(String(20))
    director = Column(String(100))
    genre = Column(String(100), index=True)
    poster_url = Column(String(500))
    description = Column(Text)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    rating = relationship("Rating", back_populates="movie", uselist=False)
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"


class Review(Base):
    """리뷰 모델"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    author_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    
    # 감성 분석 결과
    sentiment_score = Column(Float)  # -1.0 ~ 1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float)  # 0.0 ~ 1.0
    
    # Aspect-Based Sentiment (JSON)
    aspect_sentiments = Column(JSON)  # {"acting": 0.8, "plot": -0.3, ...}
    
    # Multi-Emotion (JSON)
    emotions = Column(JSON)  # {"joy": 0.7, "surprise": 0.5, ...}
    
    # Explainable AI (JSON)
    explanation = Column(JSON)  # {"important_words": [...], "shap_values": [...]}
    
    # LLM 생성 요약 (선택사항)
    llm_summary = Column(Text)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    movie = relationship("Movie", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, movie_id={self.movie_id}, sentiment={self.sentiment_label})>"


class Rating(Base):
    """영화 평점 통계"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, unique=True, index=True)
    
    # 평점 통계
    avg_sentiment = Column(Float, default=0.0)  # 평균 감정 점수
    review_count = Column(Integer, default=0)
    
    # Aspect별 평균 (JSON)
    avg_aspects = Column(JSON)  # {"acting": 0.7, "plot": 0.5, ...}
    
    # 감정 분포 (JSON)
    emotion_distribution = Column(JSON)  # {"joy": 45, "sadness": 15, ...}
    
    # 메타데이터
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    movie = relationship("Movie", back_populates="rating")
    
    def __repr__(self):
        return f"<Rating(movie_id={self.movie_id}, avg={self.avg_sentiment:.2f}, count={self.review_count})>"


class User(Base):
    """사용자 모델 (추천 시스템용)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    
    # 사용자 임베딩 (추천 시스템)
    embedding = Column(JSON)  # NCF/GNN 학습된 임베딩
    
    # 선호도 프로필
    preferences = Column(JSON)  # {"genres": [...], "directors": [...]}
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Interaction(Base):
    """사용자-영화 상호작용 (추천 시스템용)"""
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    
    # 상호작용 타입
    interaction_type = Column(String(20))  # view, like, review, watch
    
    # 암시적 피드백
    rating = Column(Float)  # 명시적 평점
    watch_duration = Column(Integer)  # 시청 시간 (초)
    completion_rate = Column(Float)  # 완료율 (0.0 ~ 1.0)
    
    # RL용 보상
    reward = Column(Float)  # Reinforcement Learning 보상
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Interaction(user={self.user_id}, movie={self.movie_id}, type={self.interaction_type})>"


class GraphNode(Base):
    """
    GNN용 그래프 노드
    영화, 배우, 감독, 장르 등을 통합 관리
    """
    __tablename__ = "graph_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String(20), nullable=False, index=True)  # movie, actor, director, genre
    node_id = Column(Integer, nullable=False)  # 원래 엔티티 ID
    name = Column(String(200), nullable=False, index=True)
    
    # 노드 임베딩 (GNN 학습)
    embedding = Column(JSON)  # 128-dim vector
    
    # 메타데이터
    properties = Column(JSON)  # 추가 속성
    
    def __repr__(self):
        return f"<GraphNode(type={self.node_type}, name='{self.name}')>"


class GraphEdge(Base):
    """
    GNN용 그래프 엣지
    노드 간 관계 정의
    """
    __tablename__ = "graph_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("graph_nodes.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("graph_nodes.id"), nullable=False, index=True)
    edge_type = Column(String(20), nullable=False, index=True)  # acted_in, directed, genre_of
    
    # 엣지 가중치
    weight = Column(Float, default=1.0)
    
    # 메타데이터
    properties = Column(JSON)
    
    def __repr__(self):
        return f"<GraphEdge(source={self.source_id}, target={self.target_id}, type={self.edge_type})>"


class ABTest(Base):
    """A/B 테스트 기록"""
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 실험 정보
    experiment_name = Column(String(100), nullable=False, index=True)
    variant = Column(String(20), nullable=False)  # control, treatment
    
    # 모델 버전
    model_version = Column(String(50))
    
    # 결과 메트릭
    metrics = Column(JSON)  # {"ctr": 0.05, "engagement_time": 120, ...}
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ABTest(experiment={self.experiment_name}, variant={self.variant})>"
