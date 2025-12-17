"""
분석 대시보드
"""

import streamlit as st
from utils.api_client import api
from utils.visualizations import (
    create_review_timeline,
    create_movie_rating_distribution,
    create_aspect_radar_chart,
    sentiment_to_emoji
)
import pandas as pd

st.set_page_config(page_title="분석 대시보드", page_icon="📊", layout="wide")

st.title("📊 분석 대시보드")

# 데이터 로딩
movies = api.get_movies(limit=1000)
all_reviews = api.get_reviews(limit=10000)

if not movies:
    st.warning("등록된 영화가 없습니다!")
    st.stop()

# 전체 통계
st.subheader("🌐 전체 통계")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("등록된 영화", len(movies))

with col2:
    st.metric("전체 리뷰", len(all_reviews))

with col3:
    if all_reviews:
        avg_sentiment = sum(r.get("sentiment_score", 0) for r in all_reviews) / len(all_reviews)
        st.metric("평균 감성", f"{avg_sentiment:.2f}")
    else:
        st.metric("평균 감성", "N/A")

with col4:
    if all_reviews:
        positive_count = sum(1 for r in all_reviews if r.get("sentiment_score", 0) > 0)
        rate = positive_count / len(all_reviews) * 100
        st.metric("긍정 비율", f"{rate:.1f}%")
    else:
        st.metric("긍정 비율", "N/A")

st.markdown("---")

# 영화별 분석
st.subheader("🎬 영화별 분석")

# 영화 선택
movie_options = {f"{m['title']} ({m['review_count']}개 리뷰)": m['id'] for m in movies}
selected_movie_str = st.selectbox(
    "분석할 영화 선택",
    options=list(movie_options.keys())
)

selected_movie_id = movie_options[selected_movie_str]
selected_movie = next(m for m in movies if m['id'] == selected_movie_id)

# 영화 정보
col1, col2 = st.columns([1, 3])

with col1:
    if selected_movie.get("poster_url"):
        try:
            st.image(selected_movie["poster_url"], use_column_width=True)
        except:
            pass

with col2:
    st.subheader(selected_movie['title'])
    st.markdown(f"**감독**: {selected_movie['director']}")
    st.markdown(f"**장르**: {selected_movie['genre']}")
    
    avg_rating = selected_movie.get('avg_rating', 0)
    review_count = selected_movie.get('review_count', 0)
    
    st.markdown(f"**평균 평점**: {sentiment_to_emoji(avg_rating)} ({avg_rating:.2f})")
    st.markdown(f"**리뷰 수**: {review_count}개")

st.markdown("---")

# 해당 영화의 리뷰
movie_reviews = api.get_reviews(movie_id=selected_movie_id, limit=1000)

if not movie_reviews:
    st.info("이 영화에 대한 리뷰가 없습니다. 첫 리뷰를 작성해보세요!")
else:
    # 시간대별 감성 변화
    st.subheader("📈 시간대별 감성 변화")
    fig = create_review_timeline(movie_reviews)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # aspect 분석 (평균)
    st.markdown("---")
    st.subheader("🎯 Aspect 평균 분석")
    
    # 모든 리뷰의 aspect 평균
    all_aspects = {}
    for review in movie_reviews:
        if review.get('aspect_sentiments'):
            for aspect, score in review['aspect_sentiments'].items():
                if aspect not in all_aspects:
                    all_aspects[aspect] = []
                all_aspects[aspect].append(score)
    
    if all_aspects:
        avg_aspects = {k: sum(v)/len(v) for k, v in all_aspects.items()}
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            fig = create_aspect_radar_chart(avg_aspects)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            aspect_names_kr = {
                "acting": "🎭 연기",
                "plot": "📖 스토리",
                "cinematography": "📸 영상미",
                "soundtrack": "🎵 음악",
                "direction": "🎬 연출",
                "screenplay": "📝 각본"
            }
            
            st.markdown("**측면별 평균 점수:**")
            for aspect, score in sorted(avg_aspects.items(), key=lambda x: x[1], reverse=True):
                aspect_kr = aspect_names_kr.get(aspect, aspect)
                emoji = sentiment_to_emoji(score)
                
                # 프로그레스 바
                normalized_score = (score + 1) / 2  # -1~1 → 0~1
                st.markdown(f"{aspect_kr}: {emoji}")
                st.progress(normalized_score, text=f"{score:.2f}")
    
    # 최근 리뷰
    st.markdown("---")
    st.subheader("📝 최근 리뷰 (최대 10개)")
    
    for review in movie_reviews[:10]:
        with st.expander(f"✍️ {review.get('author_name', 'Anonymous')} - {sentiment_to_emoji(review.get('sentiment_score', 0))}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**리뷰 내용:**")
                st.write(review.get('content', ''))
                
                if review.get('llm_summary'):
                    st.info(f"**AI 요약**: {review['llm_summary']}")
            
            with col2:
                st.markdown(f"**감성 점수**: {review.get('sentiment_score', 0):.2f}")
                st.markdown(f"**신뢰도**: {review.get('confidence', 0):.1%}")
                
                if review.get('emotions'):
                    st.markdown("**주요 감정**:")
                    emotions = review['emotions']
                    top_emotion = max(emotions.items(), key=lambda x: x[1])
                    st.markdown(f"- {top_emotion[0]}: {top_emotion[1]:.2f}")

# 전체 영화 비교
st.markdown("---")
st.subheader("🏆 영화 평점 순위")

if movies:
    fig = create_movie_rating_distribution(movies)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

# 사이드바
with st.sidebar:
    st.subheader("📊 대시보드 가이드")
    
    st.markdown("""
    ### 통계 항목
    
    - **전체 통계**: 시스템 전체 요약
    - **영화별 분석**: 개별 영화 상세
    - **시간대별 변화**: 트렌드 분석
    - **Aspect 분석**: 측면별 평가
    - **순위**: 영화 비교
    """)
    
    st.markdown("---")
    
    if movies:
        st.success(f"현재 {len(movies)}개의 영화가 등록되어 있습니다!")
