"""
⚙️ 시스템 설정 페이지
실시간으로 AI/ML 기능을 활성화/비활성화할 수 있습니다.
"""

import streamlit as st
from utils.api_client import api
import requests

st.set_page_config(page_title="시스템 설정", page_icon="⚙️", layout="wide")

st.title("⚙️ 시스템 설정")
st.markdown("토글을 변경하면 **즉시 적용**됩니다. 백엔드 재시작이 필요 없습니다!")

# API 엔드포인트
SETTINGS_API = "http://localhost:8000/api/settings/config"


def load_settings():
    """현재 설정 로드"""
    try:
        response = requests.get(SETTINGS_API, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"설정 로드 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"설정 로드 중 오류: {e}")
        return None


def save_settings(settings_data):
    """설정 저장"""
    try:
        response = requests.put(SETTINGS_API, json=settings_data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            st.error(f"설정 저장 실패: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"설정 저장 중 오류: {e}")
        return False


def reset_settings():
    """설정 초기화"""
    try:
        response = requests.post("http://localhost:8000/api/settings/config/reset", timeout=5)
        if response.status_code == 200:
            return True
        else:
            st.error(f"설정 초기화 실패: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"설정 초기화 중 오류: {e}")
        return False


# 현재 설정 로드
current_settings = load_settings()

if current_settings is None:
    st.warning("⚠️ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    st.stop()

# 세션 상태 초기화
if "settings" not in st.session_state:
    st.session_state.settings = current_settings.copy()

st.markdown("---")

# 설정 섹션
col1, col2 = st.columns(2)

with col1:
    st.subheader("🤖 AI/ML 기능 설정")
    
    # LLM
    st.markdown("### 💬 LLM (대규모 언어 모델)")
    enable_llm = st.toggle(
        "LLM 활성화",
        value=st.session_state.settings.get("enable_llm", True),
        key="llm_toggle",
        help="OpenAI/Anthropic API를 사용하여 리뷰 요약을 생성합니다."
    )
    st.caption("✅ 리뷰 요약 생성 | ⚠️ API 키 필요")
    
    st.markdown("---")
    
    # ABSA
    st.markdown("### 🎯 ABSA (세부 감성 분석)")
    enable_absa = st.toggle(
        "ABSA 활성화",
        value=st.session_state.settings.get("enable_absa", True),
        key="absa_toggle",
        help="연기, 스토리, 음악 등 세부 요소별 감성을 분석합니다."
    )
    st.caption("✅ 상세한 리뷰 분석 | 🔋 중간 리소스 사용")
    
    st.markdown("---")
    
    # Emotion Classification
    st.markdown("### 😊 Multi-Emotion Classification")
    enable_emotion = st.toggle(
        "감정 분류 활성화",
        value=st.session_state.settings.get("enable_emotion_classification", True),
        key="emotion_toggle",
        help="기쁨, 슬픔, 놀람 등 다양한 감정을 분류합니다."
    )
    st.caption("✅ 다양한 감정 분석 | 🔋 중간 리소스 사용")

with col2:
    st.subheader("🔧 성능 설정")
    
    # GPU
    st.markdown("### 🎮 GPU 사용")
    enable_gpu = st.toggle(
        "GPU 활성화",
        value=st.session_state.settings.get("enable_gpu", False),
        key="gpu_toggle",
        help="CUDA를 사용하여 AI 모델을 GPU에서 실행합니다."
    )
    if enable_gpu:
        st.caption("⚡ 빠른 처리 속도 | ⚠️ CUDA 필요")
    else:
        st.caption("🐌 CPU 사용 | ✅ 호환성 좋음")
    
    st.markdown("---")
    
    # Quantization
    st.markdown("### ⚡ Model Quantization")
    enable_quantization = st.toggle(
        "양자화 활성화",
        value=st.session_state.settings.get("enable_quantization", False),
        key="quant_toggle",
        help="모델 크기를 축소하고 속도를 향상시킵니다."
    )
    if enable_quantization:
        st.caption("⚡ 빠른 추론 | ⚠️ 정확도 약간 감소")
    else:
        st.caption("🎯 높은 정확도 | 🐌 느린 속도")
    
    st.markdown("---")
    
    # GNN
    st.markdown("### 🕸️ GNN (그래프 신경망)")
    enable_gnn = st.toggle(
        "GNN 활성화",
        value=st.session_state.settings.get("enable_gnn", False),
        key="gnn_toggle",
        help="그래프 기반 영화 추천 시스템을 사용합니다."
    )
    if enable_gnn:
        st.caption("🎯 정교한 추천 | 🔋 높은 리소스 사용")
    else:
        st.caption("⚡ 간단한 추천 | 🔋 낮은 리소스 사용")

st.markdown("---")

# 변경사항 감지
settings_changed = (
    enable_llm != current_settings.get("enable_llm") or
    enable_gpu != current_settings.get("enable_gpu") or
    enable_quantization != current_settings.get("enable_quantization") or
    enable_absa != current_settings.get("enable_absa") or
    enable_emotion != current_settings.get("enable_emotion_classification") or
    enable_gnn != current_settings.get("enable_gnn")
)

# 버튼 영역
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if settings_changed:
        st.info("💡 설정이 변경되었습니다. '적용' 버튼을 클릭하세요.")

with col2:
    if st.button("🔄 초기화", use_container_width=True, type="secondary"):
        if reset_settings():
            st.success("✅ 설정이 초기화되었습니다!")
            st.rerun()

with col3:
    if st.button("✅ 적용", use_container_width=True, type="primary", disabled=not settings_changed):
        # 새 설정 생성
        new_settings = {
            "enable_llm": enable_llm,
            "enable_gpu": enable_gpu,
            "enable_quantization": enable_quantization,
            "enable_absa": enable_absa,
            "enable_emotion_classification": enable_emotion,
            "enable_gnn": enable_gnn
        }
        
        # 설정 저장
        if save_settings(new_settings):
            st.success("✅ 설정이 즉시 적용되었습니다!")
            st.session_state.settings = new_settings
            st.rerun()

# 현재 설정 요약
st.markdown("---")
st.subheader("📊 현재 설정 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("LLM", "활성화" if current_settings.get("enable_llm") else "비활성화")
    st.metric("ABSA", "활성화" if current_settings.get("enable_absa") else "비활성화")

with col2:
    st.metric("GPU", "활성화" if current_settings.get("enable_gpu") else "비활성화")
    st.metric("Quantization", "활성화" if current_settings.get("enable_quantization") else "비활성화")

with col3:
    st.metric("Emotion", "활성화" if current_settings.get("enable_emotion_classification") else "비활성화")
    st.metric("GNN", "활성화" if current_settings.get("enable_gnn") else "비활성화")

# 사이드바 - 도움말
with st.sidebar:
    st.subheader("💡 설정 도움말")
    
    st.markdown("""
    ### 권장 설정
    
    **개발 환경 (GPU 없음):**
    - ✅ LLM: ON
    - ❌ GPU: OFF
    - ❌ Quantization: OFF
    - ✅ ABSA: ON
    - ✅ Emotion: ON
    - ❌ GNN: OFF
    
    **프로덕션 (GPU 있음):**
    - ✅ LLM: ON
    - ✅ GPU: ON
    - ✅ Quantization: ON
    - ✅ ABSA: ON
    - ✅ Emotion: ON
    - ✅ GNN: ON
    
    ### 주의사항
    - GPU 활성화 시 CUDA 설치 필요
    - LLM 사용 시 API 키 필요
    - GNN은 많은 메모리 사용
    """)
    
    st.markdown("---")
    
    st.info("""
    **💡 팁:**
    설정을 변경하면 즉시 적용되며,
    백엔드 재시작이 필요 없습니다!
    """)
