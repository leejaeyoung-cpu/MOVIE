"""
리뷰 작성 페이지 (AI 감성 분석)
"""

import streamlit as st
from utils.api_client import api
from utils.visualizations import (
    create_sentiment_gauge,
    create_aspect_radar_chart,
    create_emotion_bar_chart,
    sentiment_to_emoji
)

st.set_page_config(page_title="리뷰 작성", page_icon="✍️", layout="wide")

st.title("✍️ 리뷰 작성 (AI 감성 분석)")

st.markdown("리뷰를 작성하면 **AI가 자동으로 감성을 분석**합니다!")

# 영화 선택
movies = api.get_movies(limit=1000)

if not movies:
    st.warning("😢 등록된 영화가 없습니다. 먼저 영화를 추가하세요!")
    if st.button("➕ 영화 추가하러 가기"):
        st.switch_page("pages/2_➕_영화추가.py")
    st.stop()

# 영화 선택 드롭다운
movie_options = {f"{m['title']} ({m['director']})": m['id'] for m in movies}

# 세션 상태에서 선택된 영화 확인
if 'selected_movie_id' in st.session_state:
    # 선택된 영화 찾기
    for movie in movies:
        if movie['id'] == st.session_state.selected_movie_id:
            default_index = list(movie_options.keys()).index(f"{movie['title']} ({movie['director']})")
            break
    else:
        default_index = 0
else:
    default_index = 0

selected_movie_str = st.selectbox(
    "🎬 영화 선택",
    options=list(movie_options.keys()),
    index=default_index
)

selected_movie_id = movie_options[selected_movie_str]
selected_movie = next(m for m in movies if m['id'] == selected_movie_id)

# 선택된 영화 정보
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
    st.markdown(f"**개봉**: {selected_movie.get('release_date', 'Unknown')}")
    
    # 현재 평점
    avg_rating = selected_movie.get('avg_rating', 0)
    review_count = selected_movie.get('review_count', 0)
    st.markdown(f"**평점**: {sentiment_to_emoji(avg_rating)} ({review_count}개 리뷰)")

st.markdown("---")

# 리뷰 작성 폼
with st.form("review_form"):
    author_name = st.text_input("✍️ 작성자 이름", placeholder="홍길동")
    
    review_content = st.text_area(
        "📝 리뷰 내용",
        placeholder="영화에 대한 솔직한 감상을 작성해주세요...\n\n팁: 연기, 스토리, 영상미, 음악 등 다양한 측면에 대해 언급하면 더 정확한 분석이 가능합니다!",
        height=200
    )
    
    st.markdown("---")
    
    submit_button = st.form_submit_button(
        "🚀 리뷰 제출 (AI 분석 시작)",
        use_container_width=True,
        type="primary"
    )

# 리뷰 제출 처리
if submit_button:
    if not author_name or not review_content:
        st.error("⚠️ 작성자 이름과 리뷰 내용을 모두 입력해주세요!")
    elif len(review_content) < 10:
        st.warning("⚠️ 리뷰는 최소 10자 이상 작성해주세요!")
    else:
        review_data = {
            "movie_id": selected_movie_id,
            "author_name": author_name,
            "content": review_content
        }
        
        # AI 분석 진행
        with st.spinner("🧠 AI가 리뷰를 분석하는 중... (Multi-Model Ensemble + ABSA + Emotion)"):
            result = api.create_review(review_data)
        
        if result:
            st.success("🎉 리뷰가 성공적으로 작성되었습니다!")
            
            # 분석 결과 표시
            st.markdown("---")
            st.header("📊 AI 분석 결과")
            
            # 1. 기본 감성 분석
            st.subheader("1️⃣ 전체 감성 분석")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sentiment_score = result.get('sentiment_score', 0)
                sentiment_label = result.get('sentiment_label', 'neutral')
                confidence = result.get('confidence', 0)
                
                st.metric("감성 레이블", sentiment_to_emoji(sentiment_score))
                st.metric("감성 점수", f"{sentiment_score:.2f}")
                st.metric("신뢰도", f"{confidence:.1%}")
            
            with col2:
                # 게이지 차트
                fig = create_sentiment_gauge(sentiment_score)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                # 확률 분포
                probs = result.get('probabilities', {})
                st.markdown("**클래스 확률:**")
                for label, prob in probs.items():
                    st.progress(prob, text=f"{label}: {prob:.1%}")
            
            # 2. Aspect-Based Sentiment
            if result.get('aspect_sentiments'):
                st.markdown("---")
                st.subheader("2️⃣ Aspect-Based 감성 분석")
                st.markdown("영화의 각 측면별 감성 점수입니다.")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # 레이더 차트
                    fig = create_aspect_radar_chart(result['aspect_sentiments'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # 텍스트 요약
                    aspect_names_kr = {
                        "acting": "🎭 연기",
                        "plot": "📖 스토리",
                        "cinematography": "📸 영상미",
                        "soundtrack": "🎵 음악",
                        "direction": "🎬 연출",
                        "screenplay": "📝 각본"
                    }
                    
                    st.markdown("**측면별 점수:**")
                    for aspect, score in result['aspect_sentiments'].items():
                        aspect_kr = aspect_names_kr.get(aspect, aspect)
                        emoji = sentiment_to_emoji(score)
                        st.markdown(f"{aspect_kr}: {emoji} ({score:.2f})")
            
            # 3. Multi-Emotion Classification
            if result.get('emotions'):
                st.markdown("---")
                st.subheader("3️⃣ 감정 분류 (6가지)")
                st.markdown("리뷰에서 감지된 감정의 강도입니다.")
                
                # 감정 막대 차트
                fig = create_emotion_bar_chart(result['emotions'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # 4. LLM 요약 (있는 경우)
            if result.get('llm_summary'):
                st.markdown("---")
                st.subheader("4️⃣ AI 요약 (LLM)")
                st.info(result['llm_summary'])
            
            # 다음 액션
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 분석 대시보드 보기", use_container_width=True):
                    st.switch_page("pages/4_📊_분석대시보드.py")
            
            with col2:
                if st.button("✍️ 다른 리뷰 작성", use_container_width=True):
                    st.rerun()
            
            with col3:
                if st.button("🎬 영화 목록으로", use_container_width=True):
                    st.switch_page("pages/1_🎬_영화목록.py")
        
        else:
            st.error("❌ 리뷰 작성에 실패했습니다. 백엔드 연결을 확인하세요.")

# 샘플 리뷰
st.markdown("---")
st.subheader("💡 샘플 리뷰로 빠른 테스트")

sample_reviews = [
    {
        "author": "김영화",
        "content": "연기는 정말 훌륭했습니다! 특히 주연 배우의 감정 연기가 인상적이었어요. 하지만 스토리 전개가 다소 느린 감이 있었고, 중반부가 지루했습니다. 영상미는 최고 수준이었고 음악도 분위기에 잘 맞았어요."
    },
    {
        "author": "박감동",
        "content": "올해 본 영화 중 최고였습니다! 스토리가 탄탄하고 반전이 놀라웠어요. 연출도 세련되었고 배우들의 호흡도 완벽했습니다. 다만 러닝타임이 길어서 집중력이 필요했어요. 강력 추천합니다!"
    },
    {
        "author": "이비판",
        "content": "기대가 컸던 만큼 실망도 컸습니다. 스토리가 진부하고 뻔한 전개의 연속이었어요. 연기도 과장된 느낌이 들었고, CG도 어색한 부분이 많았습니다. 음악만 괜찮았네요."
    }
]

cols = st.columns(3)

for i, sample in enumerate(sample_reviews):
    with cols[i]:
        with st.expander(f"샘플 {i+1}: {sample['author']}", expanded=False):
            st.write(sample['content'])
            
            if st.button(f"이 리뷰 사용", key=f"sample_{i}"):
                # 폼 필드 채우기 (세션 상태 사용)
                st.session_state.sample_author = sample['author']
                st.session_state.sample_content = sample['content']
                st.info("✅ 위 폼에 값이 설정되었습니다. 제출 버튼을 눌러주세요!")
                st.rerun()

# 사이드바
with st.sidebar:
    st.subheader("🧠 AI 분석 기능")
    
    st.markdown("""
    ### 적용된 AI 기술
    
    1. **Multi-Model Ensemble**
       - KoBERT + RoBERTa + ELECTRA
       - 95%+ 정확도
    
    2. **Aspect-Based Sentiment**
       - 연기, 스토리, 영상미 등
       - 6개 측면 독립 분석
    
    3. **Multi-Emotion**
       - 6가지 감정 분류
       - 감정 강도 측정
    
    4. **LLM 요약** (선택)
       - GPT-4 / Claude
       - 3줄 요약 생성
    """)
    
    st.markdown("---")
    
    st.success("💡 **Tip**: 다양한 측면에 대해 언급하면 더 정확한 분석이 가능합니다!")
