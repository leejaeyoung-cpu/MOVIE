"""
영화 목록 페이지
"""

import streamlit as st
from utils.api_client import api
from utils.visualizations import sentiment_to_emoji, sentiment_to_color

st.set_page_config(page_title="영화 목록", page_icon="🎬", layout="wide")

st.title("🎬 영화 목록")

# 필터 섹션
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_query = st.text_input("🔍 검색", placeholder="제목, 감독, 장르로 검색...")

with col2:
    genre_filter = st.selectbox(
        "장르 필터",
        ["전체", "액션", "드라마", "코미디", "SF", "스릴러", "로맨스", "공포"]
    )

with col3:
    sort_by = st.selectbox(
        "정렬",
        ["최신순", "평점 높은순", "리뷰 많은순"]
    )

# 영화 목록 가져오기
try:
    if search_query:
        movies = api.search_movies(search_query)
    elif genre_filter != "전체":
        movies = api.get_movies(genre=genre_filter)
    else:
        movies = api.get_movies(limit=100)
    
    # 정렬
    if sort_by == "평점 높은순":
        movies = sorted(movies, key=lambda x: x.get("avg_rating", 0), reverse=True)
    elif sort_by == "리뷰 많은순":
        movies = sorted(movies, key=lambda x: x.get("review_count", 0), reverse=True)
    
    if not movies:
        st.info("😢 영화가 없습니다. '영화 추가' 페이지에서 영화를 등록하세요!")
    else:
        st.success(f"총 {len(movies)}개의 영화를 찾았습니다!")
        
        # 영화 카드 그리드 (3열)
        cols_per_row = 3
        for i in range(0, len(movies), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(movies):
                    movie = movies[i + j]
                    
                    with col:
                        # 카드 스타일
                        with st.container():
                            # 포스터 (또는 플레이스홀더)
                            if movie.get("poster_url"):
                                try:
                                    st.image(movie["poster_url"], use_column_width=True)
                                except:
                                    st.image("https://via.placeholder.com/300x450?text=No+Poster", use_column_width=True)
                            else:
                                st.image("https://via.placeholder.com/300x450?text=No+Poster", use_column_width=True)
                            
                            # 제목
                            st.subheader(movie.get("title", "Unknown"))
                            
                            # 정보
                            st.caption(f"🎬 감독: {movie.get('director', 'Unknown')}")
                            st.caption(f"🎭 장르: {movie.get('genre', 'Unknown')}")
                            st.caption(f"📅 개봉: {movie.get('release_date', 'Unknown')}")
                            
                            # 평점
                            avg_rating = movie.get("avg_rating", 0)
                            review_count = movie.get("review_count", 0)
                            
                            sentiment_emoji = sentiment_to_emoji(avg_rating)
                            sentiment_col = sentiment_to_color(avg_rating)
                            
                            st.markdown(f"⭐ **평점**: :{sentiment_col}[{sentiment_emoji}]")
                            st.caption(f"({review_count}개의 리뷰)")
                            
                            # 버튼
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if st.button("📝 리뷰 보기", key=f"view_{movie['id']}"):
                                    st.session_state.selected_movie_id = movie['id']
                                    st.switch_page("pages/4_📊_분석대시보드.py")
                            
                            with col_b:
                                if st.button("🗑️ 삭제", key=f"delete_{movie['id']}"):
                                    if api.delete_movie(movie['id']):
                                        st.success("삭제되었습니다!")
                                        st.rerun()
                                    else:
                                        st.error("삭제 실패!")
                            
                            st.markdown("---")

except Exception as e:
    st.error(f"영화를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("💡 백엔드가 실행 중인지 확인하세요!")

# 사이드바 - 통계
with st.sidebar:
    st.subheader("📊 통계")
    
    try:
        all_movies = api.get_movies(limit=1000)
        all_reviews = api.get_reviews(limit=10000)
        
        st.metric("등록된 영화", len(all_movies))
        st.metric("전체 리뷰", len(all_reviews))
        
        if all_reviews:
            avg_sentiment = sum(r.get("sentiment_score", 0) for r in all_reviews) / len(all_reviews)
            st.metric("평균 감성", f"{avg_sentiment:.2f}")
    except:
        pass
