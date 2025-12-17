"""
추천 영화 페이지
"""

import streamlit as st
from utils.api_client import api
from utils.visualizations import sentiment_to_emoji

st.set_page_config(page_title="추천 영화", page_icon="🎯", layout="wide")

st.title("🎯 AI 기반 영화 추천")

st.markdown("""
**Netflix급 추천 알고리즘**을 사용하여 당신에게 맞는 영화를 찾아드립니다!

- 🧠 Neural Collaborative Filtering (NCF)
- 🕸️ Graph Neural Networks (GNN)
- 🎮 Reinforcement Learning (RL)
- 📊 Hybrid Ensemble
""")

st.markdown("---")

# 사용자 ID 입력
user_id = st.number_input("👤 사용자 ID", min_value=1, value=1, step=1)

# 추천 받기
col1, col2 = st.columns([1, 3])

with col1:
    num_recs = st.slider("추천 영화 수", min_value=5, max_value=20, value=10)
    
    if st.button("🚀 추천 받기", use_container_width=True, type="primary"):
        with st.spinner("AI가 최적의 영화를 찾는 중..."):
            recommendations = api.get_recommendations(
                user_id=user_id,
                num_recommendations=num_recs
            )
        
        if recommendations:
            st.session_state.recommendations = recommendations
            st.success(f"✅ {len(recommendations)}개의 영화를 추천합니다!")
        else:
            st.error("추천을 생성할 수 없습니다.")

# 추천 결과 표시
if 'recommendations' in st.session_state:
    recs = st.session_state.recommendations
    
    st.markdown("---")
    st.subheader("🎬 추천 영화 목록")
    
    for i, rec in enumerate(recs):
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"### #{i+1}")
                st.metric("추천 점수", f"{rec.get('score', 0):.2f}")
            
            with col2:
                st.markdown(f"### {rec.get('title', 'Unknown')}")
                st.markdown(f"**추천 이유**: {rec.get('reason', 'N/A')}")
                
                # 영화 상세 정보 가져오기
                movie = api.get_movie(rec.get('movie_id'))
                if movie:
                    st.caption(f"감독: {movie.get('director')} | 장르: {movie.get('genre')}")
            
            with col3:
                if st.button("📝 리뷰 보기", key=f"view_{i}"):
                    st.session_state.selected_movie_id = rec.get('movie_id')
                    st.switch_page("pages/4_📊_분석대시보드.py")
            
            st.markdown("---")

# 다른 추천 방식
st.markdown("---")
st.subheader("📌 다른 추천 방식")

tab1, tab2, tab3 = st.tabs(["🔥 인기 영화", "🎭 장르별", "🔗 유사 영화"])

with tab1:
    st.markdown("### 인기 영화 (평점 및 리뷰 수 기반)")
    
    trending = api.get_trending_movies(limit=10)
    
    if trending:
        cols = st.columns(3)
        
        for i, movie in enumerate(trending):
            with cols[i % 3]:
                st.markdown(f"**{i+1}. {movie.get('title')}**")
                st.caption(f"{movie.get('genre')}")
                
                if st.button("보기", key=f"trending_{i}"):
                    st.session_state.selected_movie_id = movie.get('id')
                    st.switch_page("pages/1_🎬_영화목록.py")
    else:
        st.info("아직 인기 영화 데이터가 없습니다.")

with tab2:
    st.markdown("### 장르별 영화")
    
    genre = st.selectbox(
        "장르 선택",
        ["액션", "드라마", "코미디", "SF", "스릴러", "로맨스", "공포"]
    )
    
    if st.button("검색"):
        movies = api.get_movies(genre=genre, limit=20)
        
        if movies:
            for i, movie in enumerate(movies[:6]):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{movie.get('title')}** - {movie.get('director')}")
                
                with col2:
                    if st.button("보기", key=f"genre_{i}"):
                        st.session_state.selected_movie_id = movie.get('id')
                        st.switch_page("pages/1_🎬_영화목록.py")
        else:
            st.info("해당 장르의 영화가 없습니다.")

with tab3:
    st.markdown("### 유사 영화 찾기")
    
    all_movies = api.get_movies(limit=100)
    
    if all_movies:
        movie_options = {f"{m['title']}": m['id'] for m in all_movies}
        selected_title = st.selectbox("기준 영화", options=list(movie_options.keys()))
        
        if st.button("유사 영화 찾기"):
            base_id = movie_options[selected_title]
            similar_movies = api.get_similar_movies(base_id, limit=5)
            
            if similar_movies:
                st.success(f"'{selected_title}'와 유사한 영화:")
                
                for i, movie in enumerate(similar_movies):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{i+1}. {movie.get('title')}**")
                        st.caption(f"{movie.get('genre')}")
                    
                    with col2:
                        if st.button("보기", key=f"similar_{i}"):
                            st.session_state.selected_movie_id = movie.get('id')
                            st.switch_page("pages/1_🎬_영화목록.py")
            else:
                st.info("유사한 영화를 찾을 수 없습니다.")
    else:
        st.info("영화를 먼저 등록하세요!")

# 사이드바
with st.sidebar:
    st.subheader("🎯 추천 알고리즘")
    
    # 설정 조회
    config = api.get_config()
    
    if config and 'enabled_features' in config:
        features = config['enabled_features']
        
        st.markdown("**활성화된 기능:**")
        
        if features.get('GNN'):
            st.success("✅ Graph Neural Network")
        else:
            st.warning("⚠️ GNN 비활성화")
        
        if features.get('RL'):
            st.success("✅ Reinforcement Learning")
        else:
            st.warning("⚠️ RL 비활성화")
        
        st.markdown("---")
        
        st.markdown("""
        ### 추천 방식
        
        1. **Collaborative Filtering**
           - 유사한 사용자 기반
        
        2. **Content-Based**
           - 영화 메타데이터 기반
        
        3. **Hybrid**
           - 여러 방식 결합
        """)
    
    st.markdown("---")
    
    st.info("💡 **Tip**: 다양한 영화에 리뷰를 작성하면 더 정확한 추천을 받을 수 있습니다!")
