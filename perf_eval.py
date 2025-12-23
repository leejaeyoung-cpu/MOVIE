import sys
from pathlib import Path
import time
from datetime import datetime
import json

project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.database import SessionLocal
    from app.models import Movie, Review, Rating
    
    # Database Performance
    db = SessionLocal()
    
    # Count queries
    start = time.time()
    movie_count = db.query(Movie).count()
    movie_time = (time.time() - start) * 1000
    
    review_count = db.query(Review).count()
    rating_count = db.query(Rating).count()
    
    # Complex query
    start = time.time()
    movies_with_ratings = db.query(Movie).join(Rating).limit(10).all()
    join_time = (time.time() - start) * 1000
    
    db.close()
    
    # File System
    db_file = project_root / "movie_reviews.db"
    db_size = db_file.stat().st_size / 1024 / 1024 if db_file.exists() else 0
    
    # Calculate scores
    score = 0
    max_score = 100
    
    # Database query speed (40 points)
    if movie_time < 10:
        score += 40
        db_grade = "Excellent"
        db_points = 40
    elif movie_time < 50:
        score += 30
        db_grade = "Good"
        db_points = 30
    else:
        score += 20
        db_grade = "Fair"
        db_points = 20
    
    # Data volume (30 points)
    if movie_count >= 20:
        score += 30
        data_grade = "Excellent"
        data_points = 30
    elif movie_count >= 10:
        score += 20
        data_grade = "Good"
        data_points = 20
    else:
        score += 10
        data_grade = "Fair"
        data_points = 10
    
    # Reviews and ratings (30 points)
    if review_count > 0 and rating_count > 0:
        score += 30
        content_grade = "Excellent"
        content_points = 30
    elif rating_count > 0:
        score += 20
        content_grade = "Good"
        content_points = 20
    else:
        score += 10
        content_grade = "Fair"
        content_points = 10
    
    # Final Grade
    if score >= 90:
        grade = "A+ (Outstanding)"
    elif score >= 80:
        grade = "A (Excellent)"
    elif score >= 70:
        grade = "B (Good)"
    elif score >= 60:
        grade = "C (Fair)"
    else:
        grade = "D (Needs Improvement)"
    
    # Recommendations
    recommendations = []
    
    if movie_time > 50:
        recommendations.append("Optimize database queries or add indexes")
    
    if movie_count < 20:
        recommendations.append(f"Add more movies (current: {movie_count}, recommended: 30+)")
    
    if review_count == 0:
        recommendations.append("Add review data for testing")
    
    if rating_count == 0:
        recommendations.append("Add rating data for testing")
    
    # Save JSON result
    result = {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "database": {
            "movie_count": movie_count,
            "review_count": review_count,
            "rating_count": rating_count,
            "query_time_ms": round(movie_time, 2),
            "join_query_time_ms": round(join_time, 2),
            "db_size_mb": round(db_size, 2)
        },
        "performance": {
            "db_query_speed": {
                "grade": db_grade,
                "points": db_points,
                "max_points": 40
            },
            "data_volume": {
                "grade": data_grade,
                "points": data_points,
                "max_points": 30
            },
            "content": {
                "grade": content_grade,
                "points": content_points,
                "max_points": 30
            },
            "total_score": score,
            "max_score": max_score,
            "percentage": score,
            "final_grade": grade
        },
        "recommendations": recommendations if recommendations else ["No recommendations - Performance is good!"]
    }
    
    # Save to JSON file
    with open(project_root / "performance_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n>> Results saved to: performance_result.json")

except Exception as e:
    error_result = {
        "error": str(e),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(project_root / "performance_result.json", "w", encoding="utf-8") as f:
        json.dump(error_result, f, ensure_ascii=False, indent=2)
    
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
    import traceback
    traceback.print_exc()
