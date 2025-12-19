"""
리뷰 데이터 분석 스크립트
"""
import sqlite3
import json
from pathlib import Path
from collections import Counter

# 데이터베이스 연결
db_path = Path("backend/movie_reviews.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 리뷰 데이터 가져오기
query = """
SELECT 
    r.id,
    r.movie_id,
    m.title as movie_title,
    r.author_name,
    r.content,
    r.sentiment_score,
    r.sentiment_label,
    r.confidence,
    r.aspect_sentiments,
    r.emotions,
    r.created_at
FROM reviews r
LEFT JOIN movies m ON r.movie_id = m.id
ORDER BY r.created_at DESC
"""

cursor.execute(query)
reviews = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

# 딕셔너리 리스트로 변환
data = [dict(zip(columns, row)) for row in reviews]

print("=" * 80)
print("📊 영화 리뷰 분석 리포트")
print("=" * 80)

print(f"\n📝 총 리뷰 개수: {len(data)}개")

if len(data) > 0:
    print("\n" + "=" * 80)
    print("1️⃣ 감성 분석 통계")
    print("=" * 80)
    
    # 감성 라벨 분포
    print("\n🏷️ 감성 분류 분포:")
    sentiment_labels = [r['sentiment_label'] for r in data]
    sentiment_counts = Counter(sentiment_labels)
    for label, count in sentiment_counts.most_common():
        percentage = (count / len(data)) * 100
        print(f"  - {label}: {count}개 ({percentage:.1f}%)")
    
    # 감성 점수 통계
    scores = [r['sentiment_score'] for r in data]
    print("\n📈 감성 점수 통계 (-1.0 ~ 1.0):")
    print(f"  - 평균: {sum(scores)/len(scores):.3f}")
    print(f"  - 최대: {max(scores):.3f}")
    print(f"  - 최소: {min(scores):.3f}")
    
    # 표준편차 계산
    mean_score = sum(scores) / len(scores)
    variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5
    print(f"  - 표준편차: {std_dev:.3f}")
    
    # 신뢰도 통계
    confidences = [r['confidence'] for r in data]
    print("\n🎯 AI 분석 신뢰도:")
    print(f"  - 평균 신뢰도: {sum(confidences)/len(confidences):.3f}")
    print(f"  - 최고 신뢰도: {max(confidences):.3f}")
    print(f"  - 최저 신뢰도: {min(confidences):.3f}")
    
    print("\n" + "=" * 80)
    print("2️⃣ 영화별 리뷰 통계")
    print("=" * 80)
    
    # 영화별 통계 계산
    movie_stats = {}
    for review in data:
        title = review['movie_title']
        if title not in movie_stats:
            movie_stats[title] = {
                'count': 0,
                'scores': [],
                'confidences': []
            }
        movie_stats[title]['count'] += 1
        movie_stats[title]['scores'].append(review['sentiment_score'])
        movie_stats[title]['confidences'].append(review['confidence'])
    
    print("\n🎬 영화별 요약:")
    print(f"{'영화 제목':<30} {'리뷰 수':>8} {'평균 감성점수':>15} {'평균 신뢰도':>12}")
    print("-" * 70)
    
    # 리뷰 수로 정렬
    sorted_movies = sorted(movie_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    for title, stats in sorted_movies:
        avg_score = sum(stats['scores']) / len(stats['scores'])
        avg_conf = sum(stats['confidences']) / len(stats['confidences'])
        print(f"{title:<30} {stats['count']:>8} {avg_score:>15.3f} {avg_conf:>12.3f}")

    
    print("\n" + "=" * 80)
    print("3️⃣ 샘플 리뷰 (최근 5개)")
    print("=" * 80)
    
    for row in data[:5]:
        print(f"\n[리뷰 #{row['id']}]")
        print(f"영화: {row['movie_title']}")
        print(f"작성자: {row['author_name']}")
        print(f"내용: {row['content'][:100]}{'...' if len(row['content']) > 100 else ''}")
        print(f"감성: {row['sentiment_label']} (점수: {row['sentiment_score']:.3f}, 신뢰도: {row['confidence']:.3f})")
        
        # Aspect sentiments 파싱
        if row['aspect_sentiments']:
            try:
                aspects = json.loads(row['aspect_sentiments'])
                if aspects:
                    print("측면별 감성:", end=" ")
                    for aspect, score in aspects.items():
                        if score != 0.0:
                            print(f"{aspect}={score:.2f}", end=" ")
                    print()
            except:
                pass
        
        # Emotions 파싱
        if row['emotions']:
            try:
                emotions = json.loads(row['emotions'])
                if emotions:
                    print("감정 분석:", end=" ")
                    for emotion, score in emotions.items():
                        if score > 0.1:
                            print(f"{emotion}={score:.2f}", end=" ")
                    print()
            except:
                pass
    
    print("\n" + "=" * 80)
    print("4️⃣ AI 분석 방식 설명")
    print("=" * 80)
    
    print("""
현재 이 시스템은 **키워드 기반 간단 분석**을 사용하고 있습니다.

🔍 현재 사용 중인 방식:
  - 긍정/부정 키워드를 세어서 점수 계산
  - 빠르고 가볍지만, 정확도는 제한적
  - 외부 API 호출 없음 (비용 0원)
  - GPU/대용량 모델 다운로드 불필요

💡 config.py에서 활성화 가능한 고급 기능:
  ✅ ENABLE_LLM = True  → OpenAI/Anthropic API 사용 (비용 발생)
  ✅ SENTIMENT_MODEL = "ensemble"  → 딥러닝 모델 사용 (GPU 권장)
  ✅ ENABLE_ABSA = True  → Aspect 기반 감성 분석
  ✅ ENABLE_EMOTION_CLASSIFICATION = True  → 6가지 감정 분류

⚠️ 고급 기능을 활성화하면:
  1. LLM 사용 시 → API 키 필요 + 비용 발생
  2. 딥러닝 모델 사용 시 → 대용량 모델 다운로드 + GPU 권장

❓ 왜 기본적으로 API를 사용하지 않는가?
  → 비용 부담 없이 누구나 쉽게 실행할 수 있도록 하기 위함
  → 사용자가 필요에 따라 선택적으로 활성화 가능
""")

else:
    print("\n⚠️ 아직 작성된 리뷰가 없습니다.")
    print("💡 Streamlit 앱에서 '리뷰 작성' 페이지를 통해 리뷰를 작성해보세요!")

conn.close()

print("\n" + "=" * 80)
print("✅ 분석 완료!")
print("=" * 80)
