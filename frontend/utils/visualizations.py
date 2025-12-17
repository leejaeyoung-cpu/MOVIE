"""
시각화 유틸리티
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd


def create_sentiment_gauge(score: float) -> go.Figure:
    """
    감성 점수 게이지 차트
    
    Args:
        score: -1.0 ~ 1.0
    """
    # -1~1을 0~100으로 변환
    value = (score + 1) * 50
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "감성 점수"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "lightcoral"},
                {'range': [33, 67], 'color': "lightyellow"},
                {'range': [67, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig


def create_aspect_radar_chart(aspects: Dict[str, float]) -> go.Figure:
    """
    Aspect 기반 레이더 차트
    
    Args:
        aspects: {"acting": 0.8, "plot": -0.3, ...}
    """
    if not aspects:
        return None
    
    aspect_names_kr = {
        "acting": "연기",
        "plot": "스토리",
        "cinematography": "영상미",
        "soundtrack": "음악",
        "direction": "연출",
        "screenplay": "각본"
    }
    
    categories = [aspect_names_kr.get(k, k) for k in aspects.keys()]
    values = [(v + 1) * 50 for v in aspects.values()]  # -1~1 → 0~100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='감성 점수'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400
    )
    
    return fig


def create_emotion_bar_chart(emotions: Dict[str, float]) -> go.Figure:
    """
    감정 분포 막대 차트
    
    Args:
        emotions: {"joy": 0.7, "sadness": 0.1, ...}
    """
    if not emotions:
        return None
    
    emotion_names_kr = {
        "joy": "기쁨",
        "sadness": "슬픔",
        "anger": "분노",
        "surprise": "놀람",
        "fear": "공포",
        "disgust": "혐오"
    }
    
    emotion_colors = {
        "joy": "#FFD700",
        "sadness": "#4169E1",
        "anger": "#DC143C",
        "surprise": "#FF6347",
        "fear": "#8B008B",
        "disgust": "#228B22"
    }
    
    df = pd.DataFrame([
        {
            "emotion": emotion_names_kr.get(k, k),
            "score": v,
            "color": emotion_colors.get(k, "#808080")
        }
        for k, v in emotions.items()
    ])
    
    fig = px.bar(
        df,
        x="emotion",
        y="score",
        color="emotion",
        color_discrete_map={row["emotion"]: row["color"] for _, row in df.iterrows()},
        title="감정 분포"
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="감정",
        yaxis_title="강도",
        yaxis_range=[0, 1],
        height=400
    )
    
    return fig


def create_review_timeline(reviews: List[Dict]) -> go.Figure:
    """
    리뷰 타임라인 (시간대별 감성 변화)
    """
    if not reviews:
        return None
    
    df = pd.DataFrame(reviews)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    fig = go.Figure()
    
    # 감성 점수 라인
    fig.add_trace(go.Scatter(
        x=df['created_at'],
        y=df['sentiment_score'],
        mode='lines+markers',
        name='감성 점수',
        line=dict(color='royalblue', width=2),
        marker=dict(size=8)
    ))
    
    # 0 기준선
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="시간대별 감성 변화",
        xaxis_title="시간",
        yaxis_title="감성 점수",
        yaxis_range=[-1.1, 1.1],
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_movie_rating_distribution(movies: List[Dict]) -> go.Figure:
    """영화별 평점 분포"""
    if not movies:
        return None
    
    df = pd.DataFrame([
        {
            "title": m.get("title", "Unknown")[:20],  # 제목 20자 제한
            "rating": m.get("avg_rating", 0),
            "count": m.get("review_count", 0)
        }
        for m in movies
    ])
    
    df = df.sort_values("rating", ascending=False).head(10)
    
    fig = px.bar(
        df,
        x="title",
        y="rating",
        color="rating",
        color_continuous_scale="RdYlGn",
        title="영화별 평균 평점 (Top 10)",
        hover_data=["count"]
    )
    
    fig.update_layout(
        xaxis_title="영화",
        yaxis_title="평균 평점",
        yaxis_range=[-1, 1],
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig


def sentiment_to_emoji(score: float) -> str:
    """감성 점수를 이모지로 변환"""
    if score > 0.5:
        return "😊 긍정"
    elif score > 0:
        return "🙂 약간 긍정"
    elif score == 0:
        return "😐 중립"
    elif score > -0.5:
        return "😕 약간 부정"
    else:
        return "😞 부정"


def sentiment_to_color(score: float) -> str:
    """감성 점수를 색상으로 변환"""
    if score > 0.5:
        return "green"
    elif score > 0:
        return "lightgreen"
    elif score == 0:
        return "gray"
    elif score > -0.5:
        return "orange"
    else:
        return "red"
