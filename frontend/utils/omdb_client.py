"""
OMDb (Open Movie Database) API 클라이언트
영화 정보 및 포스터 자동 검색 기능
"""

import requests
from typing import Optional, List, Dict
import os


class OMDbClient:
    """OMDb API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: OMDb API 키 (없으면 환경 변수에서 읽기)
        """
        self.api_key = api_key or os.getenv("OMDB_API_KEY", "")
        self.base_url = "http://www.omdbapi.com"
        self.enabled = bool(self.api_key)
    
    def search_movie(self, query: str, year: Optional[str] = None) -> List[Dict]:
        """
        영화 검색
        
        Args:
            query: 검색할 영화 제목
            year: 개봉 연도 (선택사항)
        
        Returns:
            검색 결과 리스트 (최대 10개)
        """
        if not self.enabled:
            return []
        
        try:
            params = {
                "apikey": self.api_key,
                "s": query,
                "type": "movie"
            }
            
            if year:
                params["y"] = year
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # OMDb는 Response: "True" 또는 "False"로 성공 여부 표시
            if data.get("Response") == "True":
                results = data.get("Search", [])[:10]  # 최대 10개
                return results
            else:
                print(f"OMDb 검색 오류: {data.get('Error', 'Unknown error')}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"OMDb 영화 검색 오류: {e}")
            return []
    
    def get_movie_details(self, imdb_id: str) -> Optional[Dict]:
        """
        영화 상세 정보 조회 (IMDb ID 사용)
        
        Args:
            imdb_id: IMDb ID (예: "tt1375666")
        
        Returns:
            영화 상세 정보 딕셔너리 또는 None
        """
        if not self.enabled:
            return None
        
        try:
            params = {
                "apikey": self.api_key,
                "i": imdb_id,
                "plot": "full"  # 전체 줄거리
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Response") == "True":
                return data
            else:
                print(f"OMDb 상세 정보 오류: {data.get('Error', 'Unknown error')}")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"OMDb 영화 상세 정보 오류: {e}")
            return None
    
    def get_movie_by_title(self, title: str, year: Optional[str] = None) -> Optional[Dict]:
        """
        영화 제목으로 상세 정보 조회
        
        Args:
            title: 영화 제목
            year: 개봉 연도 (선택사항, 정확도 향상)
        
        Returns:
            영화 상세 정보 딕셔너리 또는 None
        """
        if not self.enabled:
            return None
        
        try:
            params = {
                "apikey": self.api_key,
                "t": title,
                "plot": "full"
            }
            
            if year:
                params["y"] = year
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("Response") == "True":
                return data
            else:
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"OMDb 영화 조회 오류: {e}")
            return None
    
    def format_search_result(self, movie: Dict) -> Dict:
        """
        검색 결과를 UI에서 사용하기 쉬운 형태로 변환
        
        Args:
            movie: OMDb 검색 결과 딕셔너리
        
        Returns:
            포맷된 영화 정보
        """
        return {
            "imdb_id": movie.get("imdbID", ""),
            "title": movie.get("Title", "제목 없음"),
            "year": movie.get("Year", ""),
            "poster_url": movie.get("Poster", "") if movie.get("Poster") != "N/A" else "",
            "type": movie.get("Type", "movie")
        }
    
    def format_movie_details(self, details: Dict) -> Dict:
        """
        영화 상세 정보를 데이터베이스 저장 형태로 변환
        
        Args:
            details: OMDb 영화 상세 정보
        
        Returns:
            데이터베이스 저장용 딕셔너리
        """
        # 개봉일 추출 (OMDb는 "Released" 필드 사용)
        released = details.get("Released", "N/A")
        
        # 날짜 형식 변환 시도 (예: "21 Jul 2010" -> "2010-07-21")
        release_date = ""
        if released != "N/A":
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(released, "%d %b %Y")
                release_date = parsed_date.strftime("%Y-%m-%d")
            except:
                # 연도만 사용
                year = details.get("Year", "")
                if year and year != "N/A":
                    release_date = f"{year}-01-01"
        
        # 감독 추출
        director = details.get("Director", "감독 정보 없음")
        if director == "N/A":
            director = "감독 정보 없음"
        
        # 장르 추출
        genre = details.get("Genre", "장르 정보 없음")
        if genre == "N/A":
            genre = "장르 정보 없음"
        
        # 포스터 URL
        poster_url = details.get("Poster", "")
        if poster_url == "N/A":
            poster_url = ""
        
        # 줄거리
        description = details.get("Plot", "")
        if description == "N/A":
            description = ""
        
        return {
            "title": details.get("Title", ""),
            "release_date": release_date,
            "director": director,
            "genre": genre,
            "poster_url": poster_url,
            "description": description,
            "imdb_id": details.get("imdbID", ""),
            "imdb_rating": details.get("imdbRating", "N/A"),
            "runtime": details.get("Runtime", "N/A")
        }


# 싱글톤 인스턴스
omdb_client = OMDbClient()
