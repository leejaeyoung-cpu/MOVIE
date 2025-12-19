"""
시스템 성능 테스트 스크립트
"""

import sys
from pathlib import Path
import time
import requests
from datetime import datetime

project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.database import SessionLocal
from app.models import Movie, Review, Rating

print("="*70)
print("🔍 시스템 성능 검토")
print("="*70)
print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. 데이터베이스 성능 테스트
print("1️⃣  데이터베이스 성능 검사")
print("-"*70)

db = SessionLocal()

# 영화 개수
start = time.time()
movie_count = db.query(Movie).count()
db_query_time = (time.time() - start) * 1000
print(f"   📊 영화 개수: {movie_count}개")
print(f"   ⏱️  쿼리 시간: {db_query_time:.2f}ms")

# 리뷰 개수
review_count = db.query(Review).count()
print(f"   💬 리뷰 개수: {review_count}개")

# 평점 개수
rating_count = db.query(Rating).count()
print(f"   ⭐ 평점 개수: {rating_count}개")

# 복잡한 쿼리 테스트
start = time.time()
movies_with_ratings = db.query(Movie).join(Rating).limit(10).all()
complex_query_time = (time.time() - start) * 1000
print(f"   🔗 JOIN 쿼리 시간 (10개): {complex_query_time:.2f}ms")

db.close()

# 2. API 응답 속도 테스트
print(f"\n2️⃣  API 응답 속도 테스트")
print("-"*70)

BASE_URL = "http://localhost:8000"

# API 엔드포인트별 테스트
endpoints = [
    ("/", "루트"),
    ("/api/movies", "영화 목록"),
    ("/api/movies/1", "영화 상세"),
    ("/api/settings/config", "설정 조회"),
]

response_times = []

for endpoint, name in endpoints:
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response_time = (time.time() - start) * 1000
        response_times.append(response_time)
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {name:20s}: {response_time:6.2f}ms (HTTP {response.status_code})")
    except Exception as e:
        print(f"   ❌ {name:20s}: 오류 - {e}")
        response_times.append(0)

if response_times:
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    min_response_time = min([t for t in response_times if t > 0])
    
    print(f"\n   📊 통계:")
    print(f"      평균: {avg_response_time:.2f}ms")
    print(f"      최소: {min_response_time:.2f}ms")
    print(f"      최대: {max_response_time:.2f}ms")

# 3. 동시 요청 테스트
print(f"\n3️⃣  동시성 테스트 (10개 동시 요청)")
print("-"*70)

import concurrent.futures

def make_request(i):
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/api/movies", timeout=10)
        return (time.time() - start) * 1000, response.status_code
    except:
        return 0, 0

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(make_request, range(10)))
total_time = (time.time() - start) * 1000

successful = sum(1 for _, status in results if status == 200)
times = [t for t, _ in results if t > 0]

print(f"   ✅ 성공: {successful}/10")
print(f"   ⏱️  총 시간: {total_time:.2f}ms")
if times:
    print(f"   📊 평균 응답: {sum(times)/len(times):.2f}ms")
    print(f"   📊 처리량: {10000/total_time:.2f} req/s")

# 4. 메모리 사용량 (추정)
print(f"\n4️⃣  메모리 사용량 추정")
print("-"*70)

try:
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"   💾 현재 프로세스 메모리: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"   📊 시스템 메모리 사용률: {psutil.virtual_memory().percent:.1f}%")
except ImportError:
    print(f"   ⚠️  psutil이 설치되지 않아 메모리 측정 불가")

# 5. 파일 시스템
print(f"\n5️⃣  파일 시스템 검사")
print("-"*70)

db_file = project_root / "backend" / "movie_reviews.db"
if db_file.exists():
    db_size = db_file.stat().st_size / 1024 / 1024
    print(f"   💾 데이터베이스 크기: {db_size:.2f} MB")
else:
    print(f"   ⚠️  데이터베이스 파일 없음")

# 6. 성능 등급 평가
print(f"\n6️⃣  성능 등급 평가")
print("-"*70)

total_score = 0
max_score = 0

# API 응답 속도 평가
if response_times:
    avg = sum(response_times) / len(response_times)
    max_score += 30
    if avg < 50:
        print(f"   ⭐⭐⭐ API 응답 속도: 우수 ({avg:.2f}ms)")
        total_score += 30
    elif avg < 100:
        print(f"   ⭐⭐ API 응답 속도: 양호 ({avg:.2f}ms)")
        total_score += 20
    else:
        print(f"   ⭐ API 응답 속도: 보통 ({avg:.2f}ms)")
        total_score += 10

# 데이터베이스 쿼리 속도 평가
max_score += 30
if db_query_time < 10:
    print(f"   ⭐⭐⭐ DB 쿼리 속도: 우수 ({db_query_time:.2f}ms)")
    total_score += 30
elif db_query_time < 50:
    print(f"   ⭐⭐ DB 쿼리 속도: 양호 ({db_query_time:.2f}ms)")
    total_score += 20
else:
    print(f"   ⭐ DB 쿼리 속도: 보통 ({db_query_time:.2f}ms)")
    total_score += 10

# 동시성 평가
max_score += 20
if successful == 10:
    print(f"   ⭐⭐⭐ 동시성 처리: 우수 (10/10)")
    total_score += 20
elif successful >= 8:
    print(f"   ⭐⭐ 동시성 처리: 양호 ({successful}/10)")
    total_score += 15
else:
    print(f"   ⭐ 동시성 처리: 보통 ({successful}/10)")
    total_score += 10

# 데이터 규모 평가
max_score += 20
if movie_count >= 20:
    print(f"   ⭐⭐⭐ 데이터 규모: 충분 ({movie_count}개 영화)")
    total_score += 20
elif movie_count >= 10:
    print(f"   ⭐⭐ 데이터 규모: 적정 ({movie_count}개 영화)")
    total_score += 15
else:
    print(f"   ⭐ 데이터 규모: 부족 ({movie_count}개 영화)")
    total_score += 10

# 최종 점수
final_score = (total_score / max_score) * 100

print(f"\n{'='*70}")
print(f"📊 최종 성능 점수: {total_score}/{max_score} ({final_score:.1f}%)")

if final_score >= 90:
    grade = "A+ (우수)"
    emoji = "🌟"
elif final_score >= 80:
    grade = "A (양호)"
    emoji = "⭐"
elif final_score >= 70:
    grade = "B (보통)"
    emoji = "👍"
else:
    grade = "C (개선 필요)"
    emoji = "⚠️"

print(f"{emoji} 등급: {grade}")
print(f"{'='*70}")

# 7. 개선 권장사항
print(f"\n7️⃣  개선 권장사항")
print("-"*70)

recommendations = []

if avg_response_time > 100:
    recommendations.append("• API 응답 시간이 느립니다. 캐싱 또는 쿼리 최적화 권장")

if db_query_time > 50:
    recommendations.append("• DB 쿼리가 느립니다. 인덱스 추가 또는 쿼리 최적화 권장")

if movie_count < 20:
    recommendations.append(f"• 영화 데이터가 부족합니다. 최소 30개 이상 권장 (현재: {movie_count}개)")

if review_count == 0:
    recommendations.append("• 리뷰 데이터가 없습니다. 테스트 리뷰 추가 권장")

if successful < 10:
    recommendations.append("• 동시 요청 처리에 문제가 있습니다. 서버 설정 확인 권장")

if recommendations:
    for rec in recommendations:
        print(f"   {rec}")
else:
    print(f"   ✅ 현재 성능이 양호합니다!")

print(f"\n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")
