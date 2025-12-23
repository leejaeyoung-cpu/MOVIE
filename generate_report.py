import json
from pathlib import Path

# Read the JSON result
project_root = Path(__file__).parent
json_file = project_root / "performance_result.json"

with open(json_file, "r", encoding="utf-8") as f:
    result = json.load(f)

# Create a formatted markdown report
report = f"""# 시스템 성능 평가 리포트

## 📋 기본 정보
- **평가 시간**: {result['timestamp']}

---

## 1️⃣ 데이터베이스 현황

| 항목 | 수량 |
|------|------|
| 영화 수 | {result['database']['movie_count']}개 |
| 리뷰 수 | {result['database']['review_count']}개 |
| 평점 수 | {result['database']['rating_count']}개 |
| DB 크기 | {result['database']['db_size_mb']} MB |

### 쿼리 성능
- **단순 쿼리 시간**: {result['database']['query_time_ms']}ms
- **JOIN 쿼리 시간**: {result['database']['join_query_time_ms']}ms

---

## 2️⃣ 성능 점수

### DB 쿼리 속도
- **등급**: {result['performance']['db_query_speed']['grade']}
- **점수**: {result['performance']['db_query_speed']['points']}/{result['performance']['db_query_speed']['max_points']}점

### 데이터 볼륨
- **등급**: {result['performance']['data_volume']['grade']}
- **점수**: {result['performance']['data_volume']['points']}/{result['performance']['data_volume']['max_points']}점

### 콘텐츠
- **등급**: {result['performance']['content']['grade']}
- **점수**: {result['performance']['content']['points']}/{result['performance']['content']['max_points']}점

---

## 🎯 최종 평가

### 총점
**{result['performance']['total_score']}/{result['performance']['max_score']}점 ({result['performance']['percentage']}%)**

### 최종 등급
**{result['performance']['final_grade']}**

---

## 💡 개선 권장사항

"""

for i, rec in enumerate(result['recommendations'], 1):
    report += f"{i}. {rec}\n"

report += "\n---\n\n## 📊 상세 분석\n\n"

# Detailed analysis
if result['performance']['percentage'] >= 90:
    report += "✅ **우수한 성능**을 보이고 있습니다. 현재 상태를 유지하면서 지속적인 모니터링이 필요합니다.\n"
elif result['performance']['percentage'] >= 80:
    report += "👍 **양호한 성능**을 보이고 있습니다. 몇 가지 개선사항을 적용하면 더 나은 성능을 얻을 수 있습니다.\n"
elif result['performance']['percentage'] >= 70:
    report += "⚠️ **보통 수준**의 성능입니다. 개선 권장사항을 참고하여 성능을 향상시킬 필요가 있습니다.\n"
else:
    report += "🔴 **성능 개선이 필요**합니다. 개선 권장사항을 우선적으로 적용해주세요.\n"

# Performance breakdown
report += "\n### 성능 분석\n\n"

# Query speed analysis
query_time = result['database']['query_time_ms']
if query_time < 10:
    report += f"- **쿼리 속도**: 매우 빠릅니다 ({query_time}ms). 최적화된 상태입니다.\n"
elif query_time < 50:
    report += f"- **쿼리 속도**: 적절한 수준입니다 ({query_time}ms).\n"
else:
    report += f"- **쿼리 속도**: 느린 편입니다 ({query_time}ms). 인덱스 추가나 쿼리 최적화가 필요합니다.\n"

# Data volume analysis
movie_count = result['database']['movie_count']
if movie_count >= 20:
    report += f"- **데이터 볼륨**: 충분한 데이터가 있습니다 ({movie_count}개 영화).\n"
elif movie_count >= 10:
    report += f"- **데이터 볼륨**: 적정 수준입니다 ({movie_count}개 영화). 추가 데이터 확보를 고려해보세요.\n"
else:
    report += f"- **데이터 볼륨**: 데이터가 부족합니다 ({movie_count}개 영화). 최소 20개 이상의 영화 데이터를 추가하세요.\n"

# Content analysis
review_count = result['database']['review_count']
rating_count = result['database']['rating_count']

if review_count > 0 and rating_count > 0:
    report += f"- **콘텐츠**: 리뷰({review_count}개)와 평점({rating_count}개) 데이터가 모두 있습니다.\n"
elif rating_count > 0:
    report += f"- **콘텐츠**: 평점 데이터({rating_count}개)는 있지만 리뷰가 없습니다. 리뷰 데이터 추가를 권장합니다.\n"
else:
    report += f"- **콘텐츠**: 리뷰와 평점 데이터가 모두 부족합니다. 테스트 데이터를 추가하세요.\n"

report += "\n---\n\n*이 리포트는 자동으로 생성되었습니다.*\n"

# Save the report
report_file = project_root / "PERFORMANCE_REPORT.md"
with open(report_file, "w", encoding="utf-8") as f:
    f.write(report)

print(f"Performance report saved to: {report_file}")
print("\n" + "="*80)
print(report)
