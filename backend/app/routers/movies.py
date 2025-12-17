"""
영화 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Movie, Rating

router = APIRouter()


# Pydantic 스키마
from pydantic import BaseModel

class MovieCreate(BaseModel):
    title: str
    release_date: str
    director: str
    genre: str
    poster_url: str
    description: str = ""

class MovieResponse(BaseModel):
    id: int
    title: str
    release_date: str
    director: str
    genre: str
    poster_url: str
    description: str
    avg_rating: float = 0.0
    review_count: int = 0
    
    class Config:
        from_attributes = True


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    """
    영화 등록
    
    **Parameters:**
    - title: 영화 제목
    - release_date: 개봉일 (YYYY-MM-DD)
    - director: 감독
    - genre: 장르
    - poster_url: 포스터 이미지 URL
    - description: 영화 설명
    """
    # 중복 체크
    existing = db.query(Movie).filter(Movie.title == movie.title).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie with this title already exists"
        )
    
    # 영화 생성
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    
    # Rating 레코드 생성
    rating = Rating(movie_id=db_movie.id)
    db.add(rating)
    db.commit()
    
    return db_movie


@router.get("/", response_model=List[MovieResponse])
async def get_movies(
    skip: int = 0,
    limit: int = 100,
    genre: str = None,
    db: Session = Depends(get_db)
):
    """
    영화 목록 조회
    
    **Parameters:**
    - skip: 건너뛸 개수 (페이지네이션)
    - limit: 최대 개수
    - genre: 장르 필터 (선택사항)
    """
    query = db.query(Movie)
    
    if genre:
        query = query.filter(Movie.genre.contains(genre))
    
    movies = query.offset(skip).limit(limit).all()
    
    # Rating 정보 추가
    result = []
    for movie in movies:
        rating = db.query(Rating).filter(Rating.movie_id == movie.id).first()
        movie_dict = {
            "id": movie.id,
            "title": movie.title,
            "release_date": movie.release_date,
            "director": movie.director,
            "genre": movie.genre,
            "poster_url": movie.poster_url,
            "description": movie.description,
            "avg_rating": rating.avg_sentiment if rating else 0.0,
            "review_count": rating.review_count if rating else 0
        }
        result.append(MovieResponse(**movie_dict))
    
    return result


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    특정 영화 조회
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    rating = db.query(Rating).filter(Rating.movie_id == movie.id).first()
    
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        release_date=movie.release_date,
        director=movie.director,
        genre=movie.genre,
        poster_url=movie.poster_url,
        description=movie.description,
        avg_rating=rating.avg_sentiment if rating else 0.0,
        review_count=rating.review_count if rating else 0
    )


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    영화 삭제
    
    관련된 리뷰와 평점도 함께 삭제됩니다 (CASCADE).
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    db.delete(movie)
    db.commit()
    
    return None


@router.get("/search/{query}")
async def search_movies(query: str, db: Session = Depends(get_db)):
    """
    영화 검색 (제목, 감독, 장르)
    """
    movies = db.query(Movie).filter(
        (Movie.title.contains(query)) |
        (Movie.director.contains(query)) |
        (Movie.genre.contains(query))
    ).all()
    
    return movies
