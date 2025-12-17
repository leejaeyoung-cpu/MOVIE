"""
통합 추천 시스템
- Neural Collaborative Filtering (NCF)
- Graph Neural Networks (GNN)
- Sequential Recommendation
- Reinforcement Learning
- Hybrid Ensemble
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Tuple, Optional
from ..config import settings, get_device


class NCFModel(nn.Module):
    """
    Neural Collaborative Filtering
    
    User와 Item의 임베딩을 학습하여 평점 예측
    """
    
    def __init__(self, num_users: int, num_items: int, embedding_dim: int = 128):
        super().__init__()
        
        # User/Item Embeddings
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        
        # MLP Layers
        layers = settings.NCF_LAYERS  # [256, 128, 64, 32]
        self.mlp = nn.Sequential()
        
        in_dim = embedding_dim * 2
        for i, out_dim in enumerate(layers):
            self.mlp.add_module(f"fc{i}", nn.Linear(in_dim, out_dim))
            self.mlp.add_module(f"relu{i}", nn.ReLU())
            self.mlp.add_module(f"dropout{i}", nn.Dropout(0.2))
            in_dim = out_dim
        
        # Output layer
        self.output = nn.Linear(layers[-1], 1)
        
        # Attention for recent interactions
        self.attention = nn.Linear(embedding_dim, 1)
        
    def forward(self, user_ids: torch.Tensor, item_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            user_ids: [batch_size]
            item_ids: [batch_size]
            
        Returns:
            predictions: [batch_size, 1]
        """
        # Embeddings
        user_emb = self.user_embedding(user_ids)  # [batch_size, emb_dim]
        item_emb = self.item_embedding(item_ids)  # [batch_size, emb_dim]
        
        # Concatenate
        concat = torch.cat([user_emb, item_emb], dim=-1)  # [batch_size, emb_dim*2]
        
        # MLP
        mlp_output = self.mlp(concat)
        
        # Prediction
        prediction = self.output(mlp_output)
        
        return torch.sigmoid(prediction)
    
    def get_user_embedding(self, user_id: int) -> torch.Tensor:
        """사용자 임베딩 추출"""
        return self.user_embedding(torch.tensor([user_id]))
    
    def get_item_embedding(self, item_id: int) -> torch.Tensor:
        """아이템 임베딩 추출"""
        return self.item_embedding(torch.tensor([item_id]))


class GraphSAGERecommender(nn.Module):
    """
    Graph Neural Network for Recommendations
    
    GraphSAGE를 사용하여 영화-배우-감독 그래프에서 추천
    """
    
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super().__init__()
        
        if not settings.ENABLE_GNN:
            return
        
        try:
            from torch_geometric.nn import SAGEConv
            
            self.conv1 = SAGEConv(in_channels, hidden_channels)
            self.conv2 = SAGEConv(hidden_channels, hidden_channels)
            self.conv3 = SAGEConv(hidden_channels, out_channels)
            
            self.dropout = nn.Dropout(0.2)
            
        except ImportError:
            print("⚠️  torch_geometric not installed. GNN disabled.")
            settings.ENABLE_GNN = False
    
    def forward(self, x, edge_index):
        """
        Forward pass
        
        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph edges [2, num_edges]
            
        Returns:
            node_embeddings: [num_nodes, out_channels]
        """
        if not settings.ENABLE_GNN:
            return x
        
        # 1st layer
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        
        # 2nd layer
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        
        # 3rd layer
        x = self.conv3(x, edge_index)
        
        return x
    
    def recommend(self, user_embedding: torch.Tensor, movie_embeddings: torch.Tensor, top_k: int = 10):
        """
        GNN 기반 추천
        
        Args:
            user_embedding: [emb_dim]
            movie_embeddings: [num_movies, emb_dim]
            top_k: 추천할 영화 수
            
        Returns:
            movie_ids: Top-K 영화 ID
            scores: 점수
        """
        # Cosine similarity
        user_emb = user_embedding.unsqueeze(0)  # [1, emb_dim]
        similarities = F.cosine_similarity(user_emb, movie_embeddings, dim=1)
        
        # Top-K
        top_scores, top_indices = torch.topk(similarities, k=top_k)
        
        return top_indices.cpu().numpy(), top_scores.cpu().numpy()


class SequentialRecommender(nn.Module):
    """
    Sequential Recommendation with Transformer
    
    사용자의 시청 히스토리 순서를 고려한 추천
    """
    
    def __init__(self, num_items: int, embedding_dim: int = 128):
        super().__init__()
        
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        self.position_embedding = nn.Embedding(settings.SEQUENCE_LENGTH, embedding_dim)
        
        if settings.SEQUENTIAL_MODEL == "transformer":
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=embedding_dim,
                nhead=8,
                dim_feedforward=512,
                dropout=0.2,
                batch_first=True
            )
            self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=3)
        elif settings.SEQUENTIAL_MODEL == "gru":
            self.encoder = nn.GRU(embedding_dim, embedding_dim, num_layers=2, batch_first=True)
        else:  # lstm
            self.encoder = nn.LSTM(embedding_dim, embedding_dim, num_layers=2, batch_first=True)
        
        self.output = nn.Linear(embedding_dim, num_items)
    
    def forward(self, item_sequence: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            item_sequence: [batch_size, seq_len]
            
        Returns:
            predictions: [batch_size, num_items]
        """
        batch_size, seq_len = item_sequence.shape
        
        # Item embeddings
        item_emb = self.item_embedding(item_sequence)  # [batch, seq_len, emb_dim]
        
        # Position embeddings
        positions = torch.arange(seq_len, device=item_sequence.device).unsqueeze(0)
        pos_emb = self.position_embedding(positions)  # [1, seq_len, emb_dim]
        
        # Add position
        x = item_emb + pos_emb
        
        # Encode sequence
        if settings.SEQUENTIAL_MODEL == "transformer":
            encoded = self.encoder(x)  # [batch, seq_len, emb_dim]
            # Last token
            encoded = encoded[:, -1, :]  # [batch, emb_dim]
        else:  # GRU/LSTM
            _, hidden = self.encoder(x)
            encoded = hidden[-1]  # [batch, emb_dim]
        
        # Output
        logits = self.output(encoded)  # [batch, num_items]
        
        return logits


class ContextualBandit:
    """
    Reinforcement Learning - Contextual Bandit
    
    사용자 컨텍스트를 고려한 최적 추천 (Exploration vs Exploitation)
    """
    
    def __init__(self, num_arms: int, context_dim: int):
        """
        Args:
            num_arms: 영화 개수
            context_dim: 컨텍스트 차원 (사용자 특징 + 시간 + 기기 등)
        """
        self.num_arms = num_arms
        self.context_dim = context_dim
        
        # Linear reward model for each arm
        self.weights = {}  # arm_id -> weight vector
        for arm in range(num_arms):
            self.weights[arm] = np.zeros(context_dim)
        
        # Confidence bounds
        self.A = {}  # arm_id -> A matrix
        self.b = {}  # arm_id -> b vector
        
        for arm in range(num_arms):
            self.A[arm] = np.identity(context_dim)
            self.b[arm] = np.zeros(context_dim)
        
        self.alpha = settings.RL_EPSILON  # Exploration parameter
    
    def select_arm(self, context: np.ndarray, candidate_arms: List[int]) -> int:
        """
        UCB (Upper Confidence Bound) 기반 arm 선택
        
        Args:
            context: [context_dim] 현재 컨텍스트
            candidate_arms: 후보 영화 ID 리스트
            
        Returns:
            selected_arm: 선택된 영화 ID
        """
        best_arm = None
        best_ucb = -float('inf')
        
        for arm in candidate_arms:
            # Predicted reward
            theta = self.weights.get(arm, np.zeros(self.context_dim))
            pred_reward = np.dot(theta, context)
            
            # Confidence bound
            A_inv = np.linalg.inv(self.A.get(arm, np.identity(self.context_dim)))
            cb = self.alpha * np.sqrt(context.T @ A_inv @ context)
            
            # UCB
            ucb = pred_reward + cb
            
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = arm
        
        return best_arm if best_arm is not None else candidate_arms[0]
    
    def update(self, arm: int, context: np.ndarray, reward: float):
        """
        보상 받은 후 모델 업데이트
        
        Args:
            arm: 선택한 영화 ID
            context: 컨텍스트
            reward: 실제 보상 (클릭=1, 시청완료=2, 좋아요=3)
        """
        # Update A and b
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context
        
        # Update weights
        A_inv = np.linalg.inv(self.A[arm])
        self.weights[arm] = A_inv @ self.b[arm]


class HybridRecommender:
    """
    Hybrid Recommendation System
    
    NCF + GNN + Sequential + RL을 조합한 최종 추천 시스템
    """
    
    def __init__(self):
        self.device = get_device()
        
        # 모델 로딩
        self.ncf_model = None
        self.gnn_model = None
        self.sequential_model = None
        self.rl_agent = None
        
        if settings.ENABLE_NCF:
            # NCF 모델 로딩 (실제로는 학습된 모델)
            pass
        
        if settings.ENABLE_GNN:
            # GNN 모델 로딩
            pass
        
        if settings.ENABLE_SEQUENTIAL:
            # Sequential 모델 로딩
            pass
        
        if settings.ENABLE_RL:
            # RL Agent 초기화
            self.rl_agent = ContextualBandit(num_arms=1000, context_dim=128)
    
    def recommend(
        self,
        user_id: int,
        num_recommendations: int = 10,
        context: Optional[Dict] = None
    ) -> List[Tuple[int, float]]:
        """
        Hybrid 추천
        
        Args:
            user_id: 사용자 ID
            num_recommendations: 추천할 영화 수
            context: 컨텍스트 정보 (시간, 기기 등)
            
        Returns:
            [(movie_id, score), ...]
        """
        recommendations = []
        
        # 1. NCF 추천
        if settings.ENABLE_NCF and self.ncf_model:
            ncf_recs = self._get_ncf_recommendations(user_id, num_recommendations * 2)
            recommendations.append(("ncf", ncf_recs, 0.3))  # 30% 가중치
        
        # 2. GNN 추천
        if settings.ENABLE_GNN and self.gnn_model:
            gnn_recs = self._get_gnn_recommendations(user_id, num_recommendations * 2)
            recommendations.append(("gnn", gnn_recs, 0.3))  # 30% 가중치
        
        # 3. Sequential 추천
        if settings.ENABLE_SEQUENTIAL and self.sequential_model:
            seq_recs = self._get_sequential_recommendations(user_id, num_recommendations * 2)
            recommendations.append(("sequential", seq_recs, 0.2))  # 20% 가중치
        
        # 4. 인기도 기반 (fallback)
        popularity_recs = self._get_popular_movies(num_recommendations * 2)
        recommendations.append(("popularity", popularity_recs, 0.2))  # 20% 가중치
        
        # Hybrid Score 계산
        movie_scores = {}
        for model_name, recs, weight in recommendations:
            for movie_id, score in recs:
                if movie_id not in movie_scores:
                    movie_scores[movie_id] = 0.0
                movie_scores[movie_id] += score * weight
        
        # 정렬 및 Top-K 선택
        sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
        candidate_movies = sorted_movies[:num_recommendations * 3]
        
        # 5. RL로 최종 선택 (선택사항)
        if settings.ENABLE_RL and self.rl_agent and context:
            context_vector = self._build_context_vector(user_id, context)
            candidate_ids = [m[0] for m in candidate_movies]
            
            final_recommendations = []
            for _ in range(num_recommendations):
                selected_id = self.rl_agent.select_arm(context_vector, candidate_ids)
                score = movie_scores[selected_id]
                final_recommendations.append((selected_id, score))
                candidate_ids.remove(selected_id)
            
            return final_recommendations
        else:
            return sorted_movies[:num_recommendations]
    
    def _get_ncf_recommendations(self, user_id: int, top_k: int) -> List[Tuple[int, float]]:
        """NCF 기반 추천"""
        # NOTE: 실제로는 학습된 NCF 모델로 추론
        # 여기서는 랜덤 스코어 반환 (데모용)
        movie_ids = list(range(1, 101))  # 영화 1-100
        scores = np.random.rand(len(movie_ids))
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [(movie_ids[i], scores[i]) for i in top_indices]
    
    def _get_gnn_recommendations(self, user_id: int, top_k: int) -> List[Tuple[int, float]]:
        """GNN 기반 추천"""
        # NOTE: 실제로는 그래프에서 이웃 노드 탐색
        movie_ids = list(range(1, 101))
        scores = np.random.rand(len(movie_ids))
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [(movie_ids[i], scores[i]) for i in top_indices]
    
    def _get_sequential_recommendations(self, user_id: int, top_k: int) -> List[Tuple[int, float]]:
        """Sequential 모델 기반 추천"""
        movie_ids = list(range(1, 101))
        scores = np.random.rand(len(movie_ids))
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [(movie_ids[i], scores[i]) for i in top_indices]
    
    def _get_popular_movies(self, top_k: int) -> List[Tuple[int, float]]:
        """인기 영화 (fallback)"""
        # NOTE: 실제로는 DB에서 리뷰 수/평점 기반
        movie_ids = list(range(1, 101))
        popularity = np.random.rand(len(movie_ids))
        top_indices = np.argsort(popularity)[-top_k:][::-1]
        return [(movie_ids[i], popularity[i]) for i in top_indices]
    
    def _build_context_vector(self, user_id: int, context: Dict) -> np.ndarray:
        """
        컨텍스트 벡터 생성
        
        Args:
            user_id: 사용자 ID
            context: {"time": "evening", "device": "mobile", ...}
            
        Returns:
            context_vector: [128-dim]
        """
        # NOTE: 실제로는 user embedding + context features
        return np.random.rand(128)


# 싱글톤 인스턴스
_recommender = None


def get_recommender() -> HybridRecommender:
    """추천 시스템 싱글톤"""
    global _recommender
    if _recommender is None:
        _recommender = HybridRecommender()
    return _recommender
