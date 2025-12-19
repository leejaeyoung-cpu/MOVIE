"""
설정 확인 스크립트
"""
import sys
sys.path.append('backend')

from app.config import settings

print("=" * 70)
print("📊 현재 시스템 설정 상태")
print("=" * 70)

print("\n🤖 AI 기능:")
print(f"   LLM 활성화: {settings.ENABLE_LLM}")
print(f"   GPU 사용: {settings.ENABLE_GPU}")
print(f"   양자화: {settings.ENABLE_QUANTIZATION}")

print("\n📊 고급 분석:")
print(f"   ABSA: {settings.ENABLE_ABSA}")
print(f"   감정 분류: {settings.ENABLE_EMOTION_CLASSIFICATION}")
print(f"   GNN 추천: {settings.ENABLE_GNN}")
print(f"   RL: {settings.ENABLE_RL}")

print("\n🧠 모델 설정:")
print(f"   감성 분석 모델: {settings.SENTIMENT_MODEL}")
print(f"   추천 모델: {settings.RECOMMENDATION_MODEL}")

if settings.ENABLE_LLM:
    print(f"\n🔑 LLM 설정:")
    print(f"   제공자: {settings.LLM_PROVIDER}")
    print(f"   모델: {settings.LLM_MODEL}")
    print(f"   API 키 설정됨: {'Yes' if settings.OPENAI_API_KEY else 'No'}")

print("\n" + "=" * 70)
print("✅ 설정 확인 완료!")
print("=" * 70)
