"""
API 클라이언트 - 백엔드와 통신
"""

import requests
from typing import List, Dict, Optional

# API Base URL
API_URL = "http://localhost:8000"


class APIClient:
    """FastAPI 백엔드와 통신하는 클라이언트"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
    
    # ========== Movies ==========
    
    def get_movies(self, skip: int = 0, limit: int = 100, genre: str = None) -> List[Dict]:
        """영화 목록 조회"""
        params = {"skip": skip, "limit": limit}
        if genre:
            params["genre"] = genre
        
        try:
            response = requests.get(f"{self.base_url}/api/movies", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting movies: {e}")
            return []
    
    def get_movie(self, movie_id: int) -> Optional[Dict]:
        """특정 영화 조회"""
        try:
            response = requests.get(f"{self.base_url}/api/movies/{movie_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting movie: {e}")
            return None
    
    def create_movie(self, movie_data: Dict) -> Optional[Dict]:
        """영화 등록"""
        try:
            response = requests.post(f"{self.base_url}/api/movies", json=movie_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating movie: {e}")
            return None
    
    def delete_movie(self, movie_id: int) -> bool:
        """영화 삭제"""
        try:
            response = requests.delete(f"{self.base_url}/api/movies/{movie_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting movie: {e}")
            return False
    
    def search_movies(self, query: str) -> List[Dict]:
        """영화 검색"""
        try:
            response = requests.get(f"{self.base_url}/api/movies/search/{query}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching movies: {e}")
            return []
    
    # ========== Reviews ==========
    
    def get_reviews(self, skip: int = 0, limit: int = 10, movie_id: int = None) -> List[Dict]:
        """리뷰 목록 조회"""
        params = {"skip": skip, "limit": limit}
        if movie_id:
            params["movie_id"] = movie_id
        
        try:
            response = requests.get(f"{self.base_url}/api/reviews", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting reviews: {e}")
            return []
    
    def create_review(self, review_data: Dict) -> Optional[Dict]:
        """
        리뷰 작성 및 감성 분석
        
        Args:
            review_data: {
                "movie_id": int,
                "author_name": str,
                "content": str
            }
            
        Returns:
            {
                "id": int,
                "sentiment_score": float,
                "sentiment_label": str,
                "aspect_sentiments": dict,
                "emotions": dict,
                ...
            }
        """
        try:
            response = requests.post(f"{self.base_url}/api/reviews", json=review_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating review: {e}")
            return None
    
    def analyze_text(self, text: str) -> Optional[Dict]:
        """텍스트 감성 분석 (리뷰 저장 없이)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/reviews/analyze",
                params={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return None
    
    # ========== Recommendations ==========
    
    def get_recommendations(
        self,
        user_id: int,
        num_recommendations: int = 10,
        context: Dict = None
    ) -> List[Dict]:
        """개인화 추천"""
        data = {
            "user_id": user_id,
            "num_recommendations": num_recommendations,
            "context": context or {}
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/recommendations", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[Dict]:
        """유사 영화 추천"""
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendations/similar/{movie_id}",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting similar movies: {e}")
            return []
    
    def get_trending_movies(self, limit: int = 10) -> List[Dict]:
        """인기 영화"""
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendations/trending",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting trending movies: {e}")
            return []
    
    def get_personalized_feed(self, user_id: int) -> Dict:
        """개인화 피드"""
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendations/personalized-feed/{user_id}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting personalized feed: {e}")
            return {"top_picks": [], "trending": [], "because_you_watched": []}
    
    # ========== Health Check ==========
    
    def health_check(self) -> bool:
        """백엔드 연결 확인"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_config(self) -> Dict:
        """백엔드 설정 조회"""
        try:
            response = requests.get(f"{self.base_url}/config")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting config: {e}")
            return {}


# 싱글톤 인스턴스
api = APIClient()
