"""
OMDb API를 사용하여 포스터가 있는 인기 영화 30개를 데이터베이스에 자동 등록
"""

import sys
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.database import SessionLocal, Base, engine
from app.models import Movie, Rating
from datetime import datetime
import requests

# OMDb API 설정
OMDB_API_KEY = "d5c11b9c"
OMDB_BASE_URL = "http://www.omdbapi.com"

# 포스터가 확실히 있는 인기 영화 30개
POPULAR_MOVIES = [
    # 클래식 명작 (10개)
    {"title": "The Shawshank Redemption", "year": "1994"},
    {"title": "The Godfather", "year": "1972"},
    {"title": "The Dark Knight", "year": "2008"},
    {"title": "Pulp Fiction", "year": "1994"},
    {"title": "Forrest Gump", "year": "1994"},
    {"title": "Inception", "year": "2010"},
    {"title": "The Matrix", "year": "1999"},
    {"title": "Goodfellas", "year": "1990"},
    {"title": "The Silence of the Lambs", "year": "1991"},
    {"title": "Schindler's List", "year": "1993"},
    
    # SF & 액션 (10개)
    {"title": "Interstellar", "year": "2014"},
    {"title": "Star Wars", "year": "1977"},
    {"title": "Avengers: Endgame", "year": "2019"},
    {"title": "Avatar", "year": "2009"},
    {"title": "Mad Max: Fury Road", "year": "2015"},
    {"title": "Gladiator", "year": "2000"},
    {"title": "The Departed", "year": "2006"},
    {"title": "Casino Royale", "year": "2006"},
    {"title": "Top Gun: Maverick", "year": "2022"},
    {"title": "John Wick", "year": "2014"},
    
    # 드라마 & 한국영화 (10개)
    {"title": "Fight Club", "year": "1999"},
    {"title": "The Prestige", "year": "2006"},
    {"title": "The Green Mile", "year": "1999"},
    {"title": "Parasite", "year": "2019"},
    {"title": "Oldboy", "year": "2003"},
    {"title": "Spirited Away", "year": "2001"},
    {"title": "Coco", "year": "2017"},
    {"title": "The Lion King", "year": "1994"},
    {"title": "Oppenheimer", "year": "2023"},
    {"title": "Dune", "year": "2021"},
]


def get_movie_from_omdb(title, year=None):
    """OMDb API에서 영화 정보 가져오기"""
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "plot": "full"
    }
    
    if year:
        params["y"] = year
    
    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") == "True":
            return data
        return None
    except Exception as e:
        print(f"API 오류: {e}")
        return None


def clear_existing_movies():
    """기존 영화 데이터 모두 삭제"""
    db = SessionLocal()
    try:
        # Rating 먼저 삭제
        db.query(Rating).delete()
        # Movie 삭제
        deleted_count = db.query(Movie).delete()
        db.commit()
        print(f"✅ 기존 영화 {deleted_count}개 삭제 완료")
        return deleted_count
    except Exception as e:
        db.rollback()
        print(f"❌ 영화 삭제 중 오류: {e}")
        return 0
    finally:
        db.close()


def populate_movies():
    """영화 데이터 채우기"""
    db = SessionLocal()
    saved_count = 0
    failed_movies = []
    
    try:
        print(f"\n🎬 {len(POPULAR_MOVIES)}개 영화 정보를 OMDb에서 가져오는 중...\n")
        
        for idx, movie_info in enumerate(POPULAR_MOVIES, 1):
            title = movie_info["title"]
            year = movie_info.get("year")
            
            print(f"[{idx}/{len(POPULAR_MOVIES)}] {title} ({year})...", end=" ")
            
            try:
                # OMDb에서 영화 정보 가져오기
                omdb_data = get_movie_from_omdb(title, year)
                
                if not omdb_data:
                    print("❌ 검색 실패")
                    failed_movies.append(f"{title} ({year})")
                    continue
                
                # 포스터 확인 - 포스터가 없으면 건너뛰기
                poster_url = omdb_data.get("Poster", "")
                if not poster_url or poster_url == "N/A":
                    print("❌ 포스터 없음 - 건너뜀")
                    failed_movies.append(f"{title} ({year}) - No Poster")
                    continue
                
                # 개봉일 처리
                released = omdb_data.get("Released", "N/A")
                release_date_str = None
                
                if released != "N/A":
                    try:
                        release_date_str = datetime.strptime(released, "%d %b %Y").strftime("%Y-%m-%d")
                    except:
                        if year and year != "N/A":
                            release_date_str = f"{year}-01-01"
                
                # 데이터베이스에 저장
                movie = Movie(
                    title=omdb_data.get("Title", title),
                    release_date=release_date_str or f"{year}-01-01",
                    director=omdb_data.get("Director", "N/A").replace("N/A", "감독 정보 없음"),
                    genre=omdb_data.get("Genre", "N/A").replace("N/A", "장르 정보 없음"),
                    poster_url=poster_url,  # 포스터 URL 확인됨
                    description=omdb_data.get("Plot", "").replace("N/A", "")
                )
                
                db.add(movie)
                db.flush()  # ID 생성
                
                # Rating 레코드도 생성
                rating = Rating(movie_id=movie.id)
                db.add(rating)
                
                db.commit()
                
                saved_count += 1
                print(f"✅ 저장 완료 (포스터: O)")
                
            except Exception as e:
                print(f"❌ 오류: {e}")
                failed_movies.append(f"{title} ({year})")
                db.rollback()
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ 총 {saved_count}개 영화 저장 완료 (모두 포스터 포함)!")
        
        if failed_movies:
            print(f"\n⚠️  실패하거나 건너뛴 영화 ({len(failed_movies)}개):")
            for movie in failed_movies:
                print(f"  - {movie}")
        
        print(f"{'='*60}\n")
        
        return saved_count
        
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("🎬 영화 데이터베이스 초기화 및 OMDb 데이터 로딩")
    print("="*60)
    
    # 데이터베이스 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 1. 기존 데이터 삭제
    print("\n1️⃣  기존 영화 데이터 삭제 중...")
    clear_existing_movies()
    
    # 2. 새 데이터 가져오기
    print("\n2️⃣  OMDb API에서 영화 데이터 가져오기...")
    saved_count = populate_movies()
    
    print(f"🎉 성공! {saved_count}개 영화가 포스터와 함께 등록되었습니다!")
    print("\n💡 Streamlit 앱을 새로고침하여 확인하세요!")
