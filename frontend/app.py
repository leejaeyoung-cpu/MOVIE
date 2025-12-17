"""
메인 Streamlit 앱
"""

import streamlit as st
from utils.api_client import api

# 페이지 설정
st.set_page_config(
    page_title="🎬 Netflix급 영화 리뷰 AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<h1 class="main-header">🎬 Netflix급 영화 리뷰 & AI 추천 시스템</h1>', unsafe_allow_html=True)

# 백엔드 연결 확인
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if api.health_check():
        st.success("✅ 백엔드 연결 성공!")
    else:
        st.error("❌ 백엔드 연결 실패! 백엔드를 먼저 실행하세요.")
        st.code("cd backend\nuvicorn app.main:app --reload", language="bash")
        st.stop()

with col2:
    # 설정 정보
    config = api.get_config()
    if config:
        with st.expander("⚙️ 시스템 설정"):
            st.json(config)

# 메인 콘텐츠
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>🧠 AI 감성 분석</h3>
        <p>Multi-Model Ensemble</p>
        <p>Aspect-Based Analysis</p>
        <p>6가지 감정 분류</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🎯 딥러닝 추천</h3>
        <p>Neural Collaborative Filtering</p>
        <p>Graph Neural Networks</p>
        <p>Reinforcement Learning</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>⚡ 성능 최적화</h3>
        <p>GPU 가속</p>
        <p>INT8 양자화 (4배 빠름)</p>
        <p>실시간 추론</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-box">
        <h3>🤖 LLM 통합</h3>
        <p>GPT-4 / Claude</p>
        <p>자동 요약</p>
        <p>반어법 감지</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 통계 섹션
st.subheader("📊 시스템 통계")

try:
    movies = api.get_movies(limit=1000)
    reviews = api.get_reviews(limit=1000)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #667eea;">{}</h2>
            <p>등록된 영화</p>
        </div>
        """.format(len(movies)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #764ba2;">{}</h2>
            <p>작성된 리뷰</p>
        </div>
        """.format(len(reviews)), unsafe_allow_html=True)
    
    with col3:
        avg_sentiment = sum(r.get("sentiment_score", 0) for r in reviews) / len(reviews) if reviews else 0
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #f093fb;">{:.2f}</h2>
            <p>평균 감성 점수</p>
        </div>
        """.format(avg_sentiment), unsafe_allow_html=True)
    
    with col4:
        positive_count = sum(1 for r in reviews if r.get("sentiment_score", 0) > 0)
        rate = (positive_count / len(reviews) * 100) if reviews else 0
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #4facfe;">{:.1f}%</h2>
            <p>긍정 비율</p>
        </div>
        """.format(rate), unsafe_allow_html=True)

except Exception as e:
    st.warning(f"통계를 불러올 수 없습니다: {e}")

st.markdown("---")

# 빠른 시작 가이드
st.subheader("🚀 빠른 시작")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**1️⃣ 영화 추가**\n\n좌측 메뉴에서 '영화 추가'를 선택하세요.")

with col2:
    st.info("**2️⃣ 리뷰 작성**\n\n'리뷰 작성'에서 AI 감성 분석을 경험하세요.")

with col3:
    st.info("**3️⃣ 추천 받기**\n\n'추천 영화'에서 개인화된 추천을 받으세요.")

# 사이드바
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3163/3163478.png", width=100)
    
    st.markdown("### 📖 사용 가이드")
    st.markdown("""
    1. **영화 목록**: 등록된 영화 보기
    2. **영화 추가**: 새 영화 등록
    3. **리뷰 작성**: AI 감성 분석
    4. **분석 대시보드**: 통계 및 시각화
    5. **추천 영화**: AI 기반 추천
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 주요 기능")
    st.markdown("""
    - ✅ Multi-Model Ensemble
    - ✅ Aspect-Based Sentiment
    - ✅ GNN 추천
    - ✅ Reinforcement Learning
    - ✅ LLM 통합
    """)
    
    st.markdown("---")
    
    st.success("💡 **Tip**: 좌측 메뉴에서 원하는 기능을 선택하세요!")
    
    st.markdown("---")
    
    st.caption("Made with ❤️ by AI")
    st.caption("Powered by FastAPI + Streamlit")
