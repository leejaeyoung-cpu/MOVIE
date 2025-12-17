"""
추천 시스템 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..services.recommender import get_recommender
from ..models import Movie
from ..config import settings

router = APIRouter()


# Pydantic 스키마
from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    user_id: int
    num_recommendations: int = 10
    context: Optional[dict] = None  # {"time": "evening", "device": "mobile"}

class RecommendationResponse(BaseModel):
    movie_id: int
    title: str
    score: float
    reason: str  # 추천 이유
    
class MovieSimple(BaseModel):
    id: int
    title: str
    genre: str
    poster_url: str


@router.post("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    개인화 영화 추천

    **Features:**
    - Neural Collaborative Filtering (NCF)
    - Graph Neural Networks (GNN)
    - Sequential Recommendation
    - Reinforcement Learning (RL)
    - Hybrid Ensemble
    
    **Parameters:**
    - user_id: 사용자 ID
    - num_recommendations: 추천할 영화 수 (기본 10개)
    - context: 컨텍스트 정보 (시간, 기기 등)
    """
    recommender = get_recommender()
    
    # 추천 생성
    recommendations = recommender.recommend(
        user_id=request.user_id,
        num_recommendations=request.num_recommendations,
        context=request.context
    )
    
    # 영화 정보 조회 및 추천 이유 생성
    result = []
    for movie_id, score in recommendations:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            # 추천 이유 생성
            reason = generate_recommendation_reason(movie, score)
            
            result.append(RecommendationResponse(
                movie_id=movie.id,
                title=movie.title,
                score=float(score),
                reason=reason
            ))
    
    return result


@router.get("/similar/{movie_id}", response_model=List[MovieSimple])
async def get_similar_movies(
    movie_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    유사 영화 추천 (Content-Based)
    
    **Parameters:**
    - movie_id: 기준 영화 ID
    - limit: 추천할 영화 수
    """
    # 기준 영화
    base_movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not base_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # 같은 장르의 영화 찾기
    similar_movies = db.query(Movie).filter(
        Movie.genre.contains(base_movie.genre),
        Movie.id != movie_id
    ).limit(limit).all()
    
    return [MovieSimple(
        id=m.id,
        title=m.title,
        genre=m.genre,
        poster_url=m.poster_url
    ) for m in similar_movies]


@router.get("/trending", response_model=List[MovieSimple])
async def get_trending_movies(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    인기 영화 (평점 및 리뷰 수 기반)
    """
    from ..models import Rating
    from sqlalchemy import desc
    
    # 평점이 높고 리뷰가 많은 영화
    popular_ratings = db.query(Rating).filter(
        Rating.review_count > 0
    ).order_by(
        desc(Rating.avg_sentiment),
        desc(Rating.review_count)
    ).limit(limit).all()
    
    result = []
    for rating in popular_ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        if movie:
            result.append(MovieSimple(
                id=movie.id,
                title=movie.title,
                genre=movie.genre,
                poster_url=movie.poster_url
            ))
    
    return result


@router.get("/by-genre/{genre}", response_model=List[MovieSimple])
async def get_movies_by_genre(
    genre: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    장르별 영화 추천
    """
    movies = db.query(Movie).filter(
        Movie.genre.contains(genre)
    ).limit(limit).all()
    
    return [MovieSimple(
        id=m.id,
        title=m.title,
        genre=m.genre,
        poster_url=m.poster_url
    ) for m in movies]


@router.get("/personalized-feed/{user_id}")
async def get_personalized_feed(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    개인화 피드 (여러 행으로 구성)
    
    Returns:
        {
            "top_picks": [...],
            "trending": [...],
            "because_you_watched": [...],
            "similar_to_liked": [...]
        }
    """
    recommender = get_recommender()
    
    # 1. Top Picks (최고 추천)
    top_picks_ids = recommender.recommend(user_id, 10)
    top_picks = [db.query(Movie).filter(Movie.id == m[0]).first() for m in top_picks_ids]
    
    # 2. Trending (인기)
    from ..models import Rating
    from sqlalchemy import desc
    trending_ratings = db.query(Rating).order_by(
        desc(Rating.review_count)
    ).limit(10).all()
    trending = [db.query(Movie).filter(Movie.id == r.movie_id).first() for r in trending_ratings]
    
    # 3. Because You Watched (시청 기록 기반)
    # NOTE: 실제로는 사용자의 시청 히스토리 조회
    byw = top_picks[:5]  # 임시
    
    return {
        "top_picks": [MovieSimple(id=m.id, title=m.title, genre=m.genre, poster_url=m.poster_url) for m in top_picks if m],
        "trending": [MovieSimple(id=m.id, title=m.title, genre=m.genre, poster_url=m.poster_url) for m in trending if m],
        "because_you_watched": [MovieSimple(id=m.id, title=m.title, genre=m.genre, poster_url=m.poster_url) for m in byw if m],
    }


def generate_recommendation_reason(movie: Movie, score: float) -> str:
    """
    추천 이유 생성
    """
    if settings.ENABLE_GNN:
        return f"그래프 기반 추천 (유사한 감독/배우): {movie.director}"
    elif settings.ENABLE_RL:
        return f"강화학습 기반 최적 추천 (스코어: {score:.2f})"
    elif settings.ENABLE_NCF:
        return f"딥러닝 기반 개인화 추천"
    else:
        return f"콘텐츠 기반 유사 영화 ({movie.genre})"
