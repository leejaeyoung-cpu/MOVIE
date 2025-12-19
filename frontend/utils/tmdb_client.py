"""
TMDB (The Movie Database) API 클라이언트
영화 정보 및 포스터 자동 검색 기능
"""

import requests
from typing import Optional, List, Dict
import os


class TMDBClient:
    """TMDB API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: TMDB API 키 (없으면 환경 변수에서 읽기)
        """
        self.api_key = api_key or os.getenv("TMDB_API_KEY", "")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p"
        self.enabled = bool(self.api_key)
    
    def search_movie(self, query: str, language: str = "ko-KR") -> List[Dict]:
        """
        영화 검색
        
        Args:
            query: 검색할 영화 제목
            language: 언어 설정 (기본값: 한국어)
        
        Returns:
            검색 결과 리스트 (최대 10개)
        """
        if not self.enabled:
            return []
        
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                "api_key": self.api_key,
                "query": query,
                "language": language,
                "page": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])[:10]  # 최대 10개
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"TMDB 영화 검색 오류: {e}")
            return []
    
    def get_movie_details(self, movie_id: int, language: str = "ko-KR") -> Optional[Dict]:
        """
        영화 상세 정보 조회
        
        Args:
            movie_id: TMDB 영화 ID
            language: 언어 설정
        
        Returns:
            영화 상세 정보 딕셔너리 또는 None
        """
        if not self.enabled:
            return None
        
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                "api_key": self.api_key,
                "language": language,
                "append_to_response": "credits"  # 감독 정보 포함
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"TMDB 영화 상세 정보 오류: {e}")
            return None
    
    def get_poster_url(self, poster_path: Optional[str], size: str = "w500") -> str:
        """
        포스터 URL 생성
        
        Args:
            poster_path: TMDB 포스터 경로
            size: 이미지 크기 (w92, w154, w185, w342, w500, w780, original)
        
        Returns:
            포스터 전체 URL 또는 빈 문자열
        """
        if not poster_path:
            return ""
        
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def format_search_result(self, movie: Dict) -> Dict:
        """
        검색 결과를 UI에서 사용하기 쉬운 형태로 변환
        
        Args:
            movie: TMDB 검색 결과 딕셔너리
        
        Returns:
            포맷된 영화 정보
        """
        return {
            "id": movie.get("id"),
            "title": movie.get("title", "제목 없음"),
            "original_title": movie.get("original_title", ""),
            "release_date": movie.get("release_date", ""),
            "overview": movie.get("overview", ""),
            "poster_path": movie.get("poster_path", ""),
            "poster_url": self.get_poster_url(movie.get("poster_path")),
            "vote_average": movie.get("vote_average", 0),
            "popularity": movie.get("popularity", 0)
        }
    
    def get_director_from_credits(self, credits: Dict) -> str:
        """
        크레딧 정보에서 감독 이름 추출
        
        Args:
            credits: 영화 크레딧 정보
        
        Returns:
            감독 이름 (여러 명이면 쉼표로 구분)
        """
        crew = credits.get("crew", [])
        directors = [person["name"] for person in crew if person.get("job") == "Director"]
        return ", ".join(directors) if directors else "감독 정보 없음"
    
    def format_movie_details(self, details: Dict) -> Dict:
        """
        영화 상세 정보를 데이터베이스 저장 형태로 변환
        
        Args:
            details: TMDB 영화 상세 정보
        
        Returns:
            데이터베이스 저장용 딕셔너리
        """
        # 장르 추출
        genres = details.get("genres", [])
        genre_str = ", ".join([g["name"] for g in genres])
        
        # 감독 추출
        credits = details.get("credits", {})
        director = self.get_director_from_credits(credits)
        
        return {
            "title": details.get("title", ""),
            "release_date": details.get("release_date", ""),
            "director": director,
            "genre": genre_str or "장르 정보 없음",
            "poster_url": self.get_poster_url(details.get("poster_path")),
            "description": details.get("overview", ""),
            "tmdb_id": details.get("id"),
            "vote_average": details.get("vote_average", 0),
            "runtime": details.get("runtime", 0)
        }


# 싱글톤 인스턴스
tmdb_client = TMDBClient()
