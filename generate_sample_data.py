"""
샘플 데이터 생성 (Direct DB)
백엔드 없이 직접 데이터베이스에 데이터 삽입
"""
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# 백엔드 경로 추가
project_root = Path(__file__).parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.database import SessionLocal, init_db
from app.models import Movie, Review, Rating

print("=" * 80)
print("🎬 영화 리뷰 AI 시스템 - 샘플 데이터 생성 (Direct DB)")
print("=" * 80)

# 데이터베이스 초기화
print("\n📦 데이터베이스 초기화 중...")
init_db()

db = SessionLocal()

# 기존 데이터 확인
existing_movies = db.query(Movie).count()
existing_reviews = db.query(Review).count()

print(f"\n현재 데이터: 영화 {existing_movies}개, 리뷰 {existing_reviews}개")

if existing_movies >= 30 and existing_reviews >= 300:
    print("\n✅ 이미 충분한 데이터가 있습니다!")
    print(f"   영화: {existing_movies}개")
    print(f"   리뷰: {existing_reviews}개")
    db.close()
    exit(0)

# 샘플 영화 데이터
sample_movies = [
    {
        "title": "기생충",
        "director": "봉준호",
        "genre": "스릴러",
        "release_date": "2019-05-30",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/5/53/Parasite_poster.jpg",
        "description": "전원 백수인 기택 가족이 부자 동네로 이사 가며 벌어지는 일"
    },
    {
        "title": "인터스텔라",
        "director": "크리스토퍼 놀란",
        "genre": "SF",
        "release_date": "2014-11-06",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/f/f6/Interstellar_poster.jpg",
        "description": "인류의 생존을 위해 블랙홀을 통과하는 우주비행사들의 이야기"
    },
    {
        "title": "범죄도시",
        "director": "강윤성",
        "genre": "액션",
        "release_date": "2017-10-03",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/a/a1/The_Outlaws_poster.jpg",
        "description": "조선족 범죄조직과 맞서는 형사들의 이야기"
    },
    {
        "title": "어벤져스: 엔드게임",
        "director": "루소 형제",
        "genre": "액션",
        "release_date": "2019-04-24",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/0/0d/Avengers_Endgame_poster.jpg",
        "description": "타노스에 맞서는 어벤져스의 최후 전투"
    },
    {
        "title": "타이타닉",
        "director": "제임스 카메론",
        "genre": "로맨스",
        "release_date": "1997-12-19",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/2/22/Titanic_poster.jpg",
        "description": "타이타닉호 침몰 사건 속 로맨스"
    },
    {
        "title": "해리 포터와 마법사의 돌",
        "director": "크리스 콜럼버스",
        "genre": "판타지",
        "release_date": "2001-11-16",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/7/70/Harry_Potter_and_the_Philosopher%27s_Stone.jpg",
        "description": "마법학교에 입학한 해리 포터의 첫 모험"
    },
    {
        "title": "겨울왕국",
        "director": "크리스 벅, 제니퍼 리",
        "genre": "애니메이션",
        "release_date": "2013-11-27",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/0/05/Frozen_poster.jpg",
        "description": "자매의 사랑과 모험을 그린 디즈니 애니메이션"
    },
    {
        "title": "쇼생크 탈출",
        "director": "프랭크 다라본트",
        "genre": "드라마",
        "release_date": "1994-09-23",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/3/33/Shawshank_redemption_ver1.jpg",
        "description": "무고하게 수감된 은행가의 탈출 이야기"
    },
    {
        "title": "인셉션",
        "director": "크리스토퍼 놀란",
        "genre": "SF",
        "release_date": "2010-07-16",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/5/56/Inception_poster.jpg",
        "description": "꿈 속에서 생각을 훔치는 도둑들의 이야기"
    },
    {
        "title": "다크 나이트",
        "director": "크리스토퍼 놀란",
        "genre": "액션",
        "release_date": "2008-07-18",
        "poster_url": "https://upload.wikimedia.org/wikipedia/ko/8/8a/Dark_Knight.jpg",
        "description": "조커와 맞서는 배트맨의 이야기"
    }
]

# 나머지 20개 영화 (간단하게)
for i in range(11, 31):
    sample_movies.append({
        "title": f"영화 제목 {i}",
        "director": f"감독 {i}",
        "genre": random.choice(["액션", "드라마", "코미디", "스릴러", "SF", "로맨스"]),
        "release_date": f"202{random.randint(0,3)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "poster_url": f"https://via.placeholder.com/300x450?text=Movie+{i}",
        "description": f"영화 {i}에 대한 설명입니다."
    })

# 샘플 리뷰 텍스트
positive_reviews = [
    "정말 감동적인 영화였습니다! 강력 추천합니다.",
    "연기, 연출, 스토리 모두 완벽했어요. 최고의 영화!",
    "몰입감이 대단했습니다. 시간 가는 줄 몰랐어요.",
    "영상미와 음악이 정말 훌륭했습니다!",
    "배우들의 연기가 너무 좋았어요. 감동의 물결!",
    "스토리 전개가 탁월했어요. 반전이 대박!",
    "촬영 기법이 너무 멋있었어요. 예술 작품 같아요.",
    "OST가 귀에 착착 감기네요. 명작입니다!",
    "완벽한 영화! 다시 봐도 좋을 것 같아요.",
    "인생 영화로 등극! 모두가 봐야 할 작품!"
]

negative_reviews = [
    "기대에 못 미쳤어요. 스토리가 산만했습니다.",
    "재미없고 지루했어요. 시간 낭비인 것 같아요.",
    "연기가 어색하고 연출이 아쉬웠습니다.",
    "스토리 전개가 너무 느려요. 졸릴 뻔 했어요.",
    "기대가 컸는데 실망이 커요. 별로였습니다.",
    "영상미는 좋은데 내용이 없어요.",
    "연기가 과장되고 부자연스러웠어요.",
    "예측 가능한 스토리. 뻔했어요.",
    "OST만 좋고 영화는 별로였습니다.",
    "돈이 아까웠어요. 추천하지 않습니다."
]

neutral_reviews = [
    "볼만했어요. 그런대로 괜찮았습니다.",
    "나쁘지 않았지만 특별하지도 않았어요.",
    "적당히 재미있었어요. 시간 때우기 좋아요.",
    "호불호가 갈릴 것 같은 영화예요.",
    "평범한 영화였습니다. 특별한 감흥은 없었어요.",
    "기대를 하지 않으면 볼만해요.",
    "괜찮은 편이지만 한 번만 볼 것 같아요.",
    "무난했어요. 크게 좋지도 나쁘지도 않았어요.",
    "심심할 때 보기 좋은 영화예요.",
    "평타는 쳤어요. 그냥 그런 영화."
]

print(f"\n🎬 영화 {len(sample_movies)}개 생성 중...")

created_movies = []
for i, movie_data in enumerate(sample_movies, 1):
    movie = Movie(
        title=movie_data["title"],
        director=movie_data["director"],
        genre=movie_data["genre"],
        release_date=datetime.strptime(movie_data["release_date"], "%Y-%m-%d").date(),
        poster_url=movie_data.get("poster_url", ""),
        description=movie_data.get("description", "")
    )
    db.add(movie)
    db.flush()  # ID 생성
    
    # Rating 생성
    rating = Rating(movie_id=movie.id)
    db.add(rating)
    
    created_movies.append(movie)
    print(f"  ✓ {i:2d}. {movie.title} (ID: {movie.id})")

db.commit()

print(f"\n✍️ 각 영화당 리뷰 10개씩 생성 중...")

authors = ["김철수", "이영희", "박민수", "정수진", "최동욱", "강지혜", "윤서연", "임재현", "한미영", "송준호"]

total_reviews = 0
for movie in created_movies:
    print(f"\n  📽️ {movie.title}")
    
    for j in range(10):
        # 랜덤 감성
        sentiment_type = random.choices(
            ['positive', 'neutral', 'negative'],
            weights=[0.6, 0.2, 0.2]  # 60% 긍정, 20% 중립, 20% 부정
        )[0]
        
        if sentiment_type == 'positive':
            content = random.choice(positive_reviews)
            sentiment_score = random.uniform(0.5, 1.0)
            sentiment_label = "positive"
        elif sentiment_type == 'negative':
            content = random.choice(negative_reviews)
            sentiment_score = random.uniform(-1.0, -0.5)
            sentiment_label = "negative"
        else:
            content = random.choice(neutral_reviews)
            sentiment_score = random.uniform(-0.3, 0.3)
            sentiment_label = "neutral"
        
        # Aspect sentiments
        aspect_sentiments = {
            "acting": round(sentiment_score + random.uniform(-0.2, 0.2), 2),
            "plot": round(sentiment_score + random.uniform(-0.2, 0.2), 2),
            "cinematography": round(sentiment_score + random.uniform(-0.2, 0.2), 2),
            "soundtrack": round(sentiment_score + random.uniform(-0.2, 0.2), 2),
            "direction": round(sentiment_score + random.uniform(-0.2, 0.2), 2),
            "screenplay": round(sentiment_score + random.uniform(-0.2, 0.2), 2)
        }
        
        # Emotions
        emotions = {
            "joy": random.uniform(0, 1) if sentiment_score > 0 else random.uniform(0, 0.3),
            "sadness": random.uniform(0, 0.3) if sentiment_score > 0 else random.uniform(0, 1),
            "anger": random.uniform(0, 0.2),
            "surprise": random.uniform(0, 0.5),
            "fear": random.uniform(0, 0.3),
            "disgust": random.uniform(0, 0.2)
        }
        
        review = Review(
            movie_id=movie.id,
            author_name=random.choice(authors),
            content=content,
            sentiment_score=round(sentiment_score, 2),
            sentiment_label=sentiment_label,
            confidence=random.uniform(0.8, 0.99),
            aspect_sentiments=aspect_sentiments,
            emotions=emotions,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        db.add(review)
        total_reviews += 1
        
        emoji = "😊" if sentiment_label == "positive" else ("😞" if sentiment_label == "negative" else "😐")
        print(f"    ✅ {j+1:2d}. {review.author_name}: {emoji} {sentiment_label} ({sentiment_score:.2f})")
    
    # Rating 업데이트
    reviews = db.query(Review).filter(Review.movie_id == movie.id).all()
    rating = db.query(Rating).filter(Rating.movie_id == movie.id).first()
    
    if rating and reviews:
        rating.review_count = len(reviews)
        rating.avg_sentiment = sum(r.sentiment_score for r in reviews) / len(reviews)
        
        # 평균 aspect sentiments
        avg_aspects = {}
        for aspect in ["acting", "plot", "cinematography", "soundtrack", "direction", "screenplay"]:
            scores = [r.aspect_sentiments.get(aspect, 0) for r in reviews if r.aspect_sentiments]
            avg_aspects[aspect] = round(sum(scores) / len(scores), 2) if scores else 0
        rating.avg_aspects = avg_aspects

db.commit()

# 최종 카운트
final_movies = db.query(Movie).count()
final_reviews = db.query(Review).count()

db.close()

print("\n" + "=" * 80)
print("🎉 샘플 데이터 생성 완료!")
print("=" * 80)
print(f"\n📊 생성 결과:")
print(f"  ✅ 영화: {final_movies}개")
print(f"  ✅ 리뷰: {final_reviews}개")
print(f"  ✅ 평균: {final_reviews/final_movies:.1f}개/영화")
print("\n" + "=" * 80)
