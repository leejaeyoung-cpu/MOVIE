"""
리뷰 API 라우터 (감성 분석 통합)
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import Review, Movie, Rating
from ..services.sentiment_analyzer import get_sentiment_analyzer, get_absa_analyzer, get_emotion_classifier
from ..services.llm_service import get_llm_service
from ..config import settings

router = APIRouter()


# Pydantic 스키마
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    movie_id: int
    author_name: str
    content: str

class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    author_name: str
    content: str
    sentiment_score: float
    sentiment_label: str
    confidence: float
    aspect_sentiments: dict = {}
    emotions: dict = {}
    llm_summary: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    리뷰 작성 및 감성 분석
    
    **Features:**
    - Multi-Model Ensemble 감성 분석
    - Aspect-Based Sentiment (연기, 스토리, 영상미 등)
    - Multi-Emotion Classification (6가지 감정)
    - LLM 요약 생성 (선택사항)
    
    **Parameters:**
    - movie_id: 영화 ID
    - author_name: 작성자 이름
    - content: 리뷰 내용
    """
    # 영화 존재 확인
    movie = db.query(Movie).filter(Movie.id == review.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # 1. 감성 분석
    sentiment_analyzer = get_sentiment_analyzer()
    sentiment_result = sentiment_analyzer.analyze(review.content)
    
    # 2. Aspect-Based Sentiment
    aspect_sentiments = {}
    if settings.ENABLE_ABSA:
        absa_analyzer = get_absa_analyzer()
        aspect_sentiments = absa_analyzer.analyze(review.content)
    
    # 3. Emotion Classification
    emotions = {}
    if settings.ENABLE_EMOTION_CLASSIFICATION:
        emotion_classifier = get_emotion_classifier()
        emotions = emotion_classifier.analyze(review.content, sentiment_result)
    
    # 4. LLM 요약 (비동기, 선택사항)
    llm_summary = None
    if settings.ENABLE_LLM:
        llm_service = get_llm_service()
        try:
            import asyncio
            llm_summary = await llm_service.summarize_review(review.content)
        except:
            pass  # LLM 실패 시 무시
    
    # 리뷰 저장
    db_review = Review(
        movie_id=review.movie_id,
        author_name=review.author_name,
        content=review.content,
        sentiment_score=sentiment_result["sentiment_score"],
        sentiment_label=sentiment_result["sentiment_label"],
        confidence=sentiment_result["confidence"],
        aspect_sentiments=aspect_sentiments,
        emotions=emotions,
        llm_summary=llm_summary
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # 평점 통계 업데이트 (백그라운드)
    background_tasks.add_task(update_movie_rating, review.movie_id, db)
    
    return db_review


@router.get("/", response_model=List[ReviewResponse])
async def get_reviews(
    skip: int = 0,
    limit: int = 10,
    movie_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    리뷰 목록 조회
    
    **Parameters:**
    - skip: 건너뛸 개수
    - limit: 최대 개수 (기본 10개)
    - movie_id: 특정 영화의 리뷰만 조회 (선택사항)
    """
    query = db.query(Review).order_by(Review.created_at.desc())
    
    if movie_id:
        query = query.filter(Review.movie_id == movie_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """특정 리뷰 조회"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """리뷰 삭제"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    movie_id = review.movie_id
    db.delete(review)
    db.commit()
    
    # 평점 통계 업데이트
    background_tasks.add_task(update_movie_rating, movie_id, db)
    
    return None


@router.post("/analyze", response_model=dict)
async def analyze_text(text: str):
    """
    텍스트 감성 분석 (리뷰 저장 없이)
    
    디버깅 및 테스트용 엔드포인트
    """
    sentiment_analyzer = get_sentiment_analyzer()
    result = sentiment_analyzer.analyze(text)
    
    if settings.ENABLE_ABSA:
        absa_analyzer = get_absa_analyzer()
        result["aspects"] = absa_analyzer.analyze(text)
    
    if settings.ENABLE_EMOTION_CLASSIFICATION:
        emotion_classifier = get_emotion_classifier()
        result["emotions"] = emotion_classifier.analyze(text, result)
    
    return result


def update_movie_rating(movie_id: int, db: Session):
    """
    영화 평점 통계 업데이트 (백그라운드 작업)
    """
    # 모든 리뷰 조회
    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    
    if not reviews:
        return
    
    # 평균 계산
    avg_sentiment = sum(r.sentiment_score for r in reviews) / len(reviews)
    
    # Aspect별 평균
    avg_aspects = {}
    if settings.ENABLE_ABSA:
        all_aspects = {}
        for review in reviews:
            if review.aspect_sentiments:
                for aspect, score in review.aspect_sentiments.items():
                    if aspect not in all_aspects:
                        all_aspects[aspect] = []
                    all_aspects[aspect].append(score)
        
        for aspect, scores in all_aspects.items():
            avg_aspects[aspect] = sum(scores) / len(scores)
    
    # 감정 분포
    emotion_distribution = {}
    if settings.ENABLE_EMOTION_CLASSIFICATION:
        for emotion in ["joy", "sadness", "anger", "surprise", "fear", "disgust"]:
            count = sum(1 for r in reviews if r.emotions and r.emotions.get(emotion, 0) > 0.5)
            emotion_distribution[emotion] = count
    
    # Rating 업데이트
    rating = db.query(Rating).filter(Rating.movie_id == movie_id).first()
    if rating:
        rating.avg_sentiment = avg_sentiment
        rating.review_count = len(reviews)
        rating.avg_aspects = avg_aspects
        rating.emotion_distribution = emotion_distribution
        db.commit()
