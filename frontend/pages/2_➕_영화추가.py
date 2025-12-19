"""
영화 추가 페이지
OMDb API를 활용한 자동 검색 및 수동 입력 지원
"""

import streamlit as st
from datetime import date
from utils.api_client import api
from utils.omdb_client import omdb_client

st.set_page_config(page_title="영화 추가", page_icon="➕", layout="wide")

st.title("➕ 영화 추가")

st.markdown("새로운 영화를 데이터베이스에 등록합니다.")

# 세션 상태 초기화
if "omdb_search_results" not in st.session_state:
    st.session_state.omdb_search_results = []
if "selected_omdb_movie" not in st.session_state:
    st.session_state.selected_omdb_movie = None
if "auto_filled" not in st.session_state:
    st.session_state.auto_filled = False

# ==================== OMDb 자동 검색 섹션 ====================
st.markdown("---")
st.subheader("🔍 OMDb 자동 검색")

if omdb_client.enabled:
    st.info("💡 영화 제목을 검색하면 포스터, 감독, 장르 등의 정보가 자동으로 입력됩니다!")
    
    col_search, col_year, col_btn = st.columns([2, 1, 1])
    
    with col_search:
        search_query = st.text_input(
            "영화 제목 검색",
            placeholder="예: Inception, 기생충",
            key="omdb_search_input"
        )
    
    with col_year:
        search_year = st.text_input(
            "연도 (선택)",
            placeholder="2010",
            key="omdb_year_input"
        )
    
    with col_btn:
        if st.button("🔍 검색", use_container_width=True, type="primary"):
            if search_query:
                with st.spinner("OMDb에서 영화를 검색하는 중..."):
                    results = omdb_client.search_movie(
                        search_query, 
                        year=search_year if search_year else None
                    )
                    st.session_state.omdb_search_results = [
                        omdb_client.format_search_result(movie) for movie in results
                    ]
                
                if not st.session_state.omdb_search_results:
                    st.warning("❌ 검색 결과가 없습니다. 영어 제목이나 다른 검색어를 시도해보세요.")
    
    # 검색 결과 표시
    if st.session_state.omdb_search_results:
        st.markdown("#### 📋 검색 결과")
        
        # 5개씩 표시
        for i in range(0, min(5, len(st.session_state.omdb_search_results))):
            movie = st.session_state.omdb_search_results[i]
            
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if movie["poster_url"]:
                        try:
                            st.image(movie["poster_url"], use_container_width=True)
                        except:
                            st.markdown("🎬")
                    else:
                        st.markdown("🎬\n\n(포스터 없음)")
                
                with col2:
                    st.markdown(f"**{movie['title']}** ({movie['year']})")
                    st.caption(f"IMDb ID: {movie['imdb_id']}")
                
                with col3:
                    if st.button("선택", key=f"select_{movie['imdb_id']}", use_container_width=True):
                        # 상세 정보 가져오기
                        with st.spinner("영화 상세 정보를 가져오는 중..."):
                            details = omdb_client.get_movie_details(movie['imdb_id'])
                            
                            if details:
                                st.session_state.selected_omdb_movie = omdb_client.format_movie_details(details)
                                st.session_state.auto_filled = True
                                st.success(f"✅ '{movie['title']}' 정보를 가져왔습니다! 아래에서 확인 후 등록하세요.")
                                st.rerun()
                
                st.markdown("---")

else:
    st.warning("""
    ⚠️ OMDb API 키가 설정되지 않았습니다.
    
    **OMDb API 키 설정 방법:**
    1. http://www.omdbapi.com/apikey.aspx 방문
    2. 무료 API 키 신청 (이메일 입력만 하면 됨)
    3. 이메일로 받은 API 키 활성화
    4. 백엔드 디렉토리에 `.env` 파일 생성 후 추가:
       ```
       OMDB_API_KEY=your_api_key_here
       ```
    5. 서버 재시작
    
    **장점:**
    - ✅ 회원가입 없이 즉시 발급
    - ✅ 무료 (하루 1,000회 요청)
    - ✅ 간단한 설정
    
    API 키 없이도 수동으로 영화 정보를 입력할 수 있습니다.
    """)

# ==================== 수동 입력 폼 ====================
st.markdown("---")
st.subheader("📝 영화 정보 입력")

# 입력 폼
with st.form("add_movie_form"):
    col1, col2 = st.columns(2)
    
    # 자동 입력된 값 사용 또는 기본값
    default_values = st.session_state.selected_omdb_movie if st.session_state.auto_filled else {}
    
    with col1:
        title = st.text_input(
            "🎬 영화 제목 *",
            value=default_values.get("title", ""),
            placeholder="예: 인셉션"
        )
        director = st.text_input(
            "🎥 감독 *",
            value=default_values.get("director", ""),
            placeholder="예: 크리스토퍼 놀란"
        )
        
        # 개봉일 처리
        release_date_str = default_values.get("release_date", "")
        if release_date_str and release_date_str != "":
            try:
                from datetime import datetime
                release_date_default = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            except:
                release_date_default = date.today()
        else:
            release_date_default = date.today()
        
        release_date = st.date_input("📅 개봉일 *", value=release_date_default)
    
    with col2:
        genre = st.text_input(
            "🎭 장르 *",
            value=default_values.get("genre", ""),
            placeholder="예: SF, 스릴러"
        )
        
        # 포스터 입력 섹션
        st.markdown("#### 🖼️ 포스터 이미지")
        st.caption("URL을 입력하거나 이미지를 업로드하세요.")
        
        # 1. URL 입력
        poster_url_input = st.text_input(
            "포스터 URL",
            value=default_values.get("poster_url", ""),
            placeholder="https://example.com/poster.jpg",
            label_visibility="collapsed"
        )

        # 2. 파일 업로드 (드래그 앤 드롭)
        uploaded_file = st.file_uploader(
            "또는 이미지 파일 업로드 (Drag & Drop)",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        
        poster_url = poster_url_input
        
        # 파일이 업로드되면 URL보다 우선순위 적용 및 Base64 변환
        if uploaded_file is not None:
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                
                image = Image.open(uploaded_file)
                
                # 리사이즈 (용량 최적화, 최대 너비 400px)
                max_width = 400
                if image.width > max_width:
                    ratio = max_width / image.width
                    new_size = (max_width, int(image.height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                buffered = BytesIO()
                # 포맷 결정
                fmt = uploaded_file.type.split('/')[-1].upper()
                if fmt == 'JPG': fmt = 'JPEG'
                if fmt not in ['JPEG', 'PNG', 'WEBP']: fmt = 'JPEG'
                
                image.save(buffered, format=fmt)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                poster_url = f"data:image/{fmt.lower()};base64,{img_str}"
                
            except Exception as e:
                st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")

        # 3. 미리보기
        if poster_url:
            try:
                st.image(poster_url, width=200, caption="포스터 미리보기")
            except:
                st.warning("이미지를 불러올 수 없습니다. URL을 확인해주세요.")
    
    description = st.text_area(
        "📝 영화 설명",
        value=default_values.get("description", ""),
        placeholder="영화에 대한 간단한 설명을 입력하세요...",
        height=150
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit_button = st.form_submit_button("✅ 영화 등록", use_container_width=True, type="primary")
    
    with col2:
        if st.form_submit_button("🔄 초기화", use_container_width=True):
            st.session_state.auto_filled = False
            st.session_state.selected_omdb_movie = None
            st.rerun()

# 제출 처리
if submit_button:
    # 필수 필드 검증
    if not all([title, director, genre]):
        st.error("⚠️ 필수 항목을 모두 입력해주세요! (제목, 감독, 장르)")
    else:
        # 영화 데이터 생성
        movie_data = {
            "title": title,
            "release_date": str(release_date),
            "director": director,
            "genre": genre,
            "poster_url": poster_url or "",
            "description": description or ""
        }
        
        # API 호출
        with st.spinner("영화를 등록하는 중..."):
            result = api.create_movie(movie_data)
        
        if result:
            st.success(f"🎉 영화 '{title}'이(가) 성공적으로 등록되었습니다!")
            
            # 세션 상태 초기화
            st.session_state.auto_filled = False
            st.session_state.selected_omdb_movie = None
            st.session_state.omdb_search_results = []
            
            # 등록된 영화 정보 표시
            with st.expander("📄 등록된 영화 정보", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if poster_url:
                        try:
                            st.image(poster_url, use_container_width=True)
                        except:
                            pass
                
                with col2:
                    st.markdown(f"**제목**: {result.get('title')}")
                    st.markdown(f"**감독**: {result.get('director')}")
                    st.markdown(f"**장르**: {result.get('genre')}")
                    st.markdown(f"**개봉일**: {result.get('release_date')}")
                    st.markdown(f"**ID**: {result.get('id')}")
            
            # 다음 액션 버튼
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 이 영화에 리뷰 작성하기", use_container_width=True):
                    st.session_state.selected_movie_id = result.get('id')
                    st.switch_page("pages/3_✍️_리뷰작성.py")
            
            with col2:
                if st.button("🎬 영화 목록 보기", use_container_width=True):
                    st.switch_page("pages/1_🎬_영화목록.py")
        else:
            st.error("❌ 영화 등록에 실패했습니다. 백엔드 연결을 확인하세요.")

# 샘플 영화 데이터
st.markdown("---")
st.subheader("💡 샘플 영화 빠른 등록")

st.markdown("테스트용으로 유명한 영화를 빠르게 등록할 수 있습니다.")

sample_movies = [
    {
        "title": "인셉션",
        "director": "크리스토퍼 놀란",
        "release_date": "2010-07-21",
        "genre": "SF, 스릴러",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/6/67/%EC%9D%B8%EC%85%89%EC%85%98_%ED%8F%AC%EC%8A%A4%ED%84%B0.jpg",
        "description": "꿈 속의 꿈으로 들어가 생각을 훔치고 심는 특수 요원의 이야기"
    },
    {
        "title": "기생충",
        "director": "봉준호",
        "release_date": "2019-05-30",
        "genre": "드라마, 스릴러",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/5/53/%EA%B8%B0%EC%83%9D%EC%B6%A9_%ED%8F%AC%EC%8A%A4%ED%84%B0.jpg",
        "description": "전원 백수인 기택 가족과 IT 기업 CEO 박 사장 가족의 만남"
    },
    {
        "title": "인터스텔라",
        "director": "크리스토퍼 놀란",
        "release_date": "2014-11-06",
        "genre": "SF, 드라마",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/4/4a/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC.jpg",
        "description": "황폐해진 지구를 떠나 새로운 행성을 찾아 떠나는 우주 탐험"
    }
]

cols = st.columns(3)

for i, sample in enumerate(sample_movies):
    with cols[i]:
        with st.container():
            if sample.get("poster_url"):
                try:
                    st.image(sample["poster_url"], use_container_width=True)
                except:
                    pass
            
            st.markdown(f"**{sample['title']}**")
            st.caption(f"{sample['director']} | {sample['genre']}")
            
            if st.button(f"등록하기", key=f"sample_{i}", use_container_width=True):
                result = api.create_movie(sample)
                if result:
                    st.success(f"✅ {sample['title']} 등록 완료!")
                    st.rerun()
                else:
                    st.error("등록 실패 (이미 존재하는 영화일 수 있습니다)")

# 사이드바 - 가이드
with st.sidebar:
    st.subheader("📖 사용 가이드")
    
    st.markdown("""
    ### 🔍 OMDb 자동 검색
    1. 영화 제목 입력 (영어 권장)
    2. 연도 입력 (선택사항, 정확도 향상)
    3. 검색 후 원하는 영화 선택
    4. 자동으로 모든 정보 입력됨
    
    ### 📝 수동 입력
    - 검색 결과가 없거나 API 키가 없을 때 사용
    
    ### 필수 입력 항목
    - 🎬 영화 제목
    - 🎥 감독
    - 🎭 장르
    
    ### 선택 항목
    - 🖼️ 포스터 URL
    - 📝 영화 설명
    
    ### 💡 팁
    - OMDb는 **영어 제목**으로 검색하는 것이 가장 정확합니다
    - 한국 영화는 영어 제목이 없으면 수동 입력 필요
    - 연도를 함께 입력하면 검색 정확도 향상
    - API 키 발급은 1분이면 완료!
    """)
    
    st.markdown("---")
    
    st.info("💡 영화 등록 후 바로 리뷰를 작성할 수 있습니다!")
