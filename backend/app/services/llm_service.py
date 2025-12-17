"""
LLM Integration Service
- OpenAI GPT-4
- Anthropic Claude
- 리뷰 요약, 감성 분석, 설명 생성
"""

from typing import Dict, List, Optional
import asyncio
from ..config import settings

# LLM 클라이언트 (선택적 import)
try:
    if settings.LLM_PROVIDER == "openai":
        from openai import AsyncOpenAI
        llm_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    elif settings.LLM_PROVIDER == "anthropic":
        from anthropic import AsyncAnthropic
        llm_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
    else:
        llm_client = None
except ImportError:
    print("⚠️  LLM SDK not installed. LLM features disabled.")
    llm_client = None


class LLMService:
    """
    LLM 통합 서비스
    
    Features:
    - Zero-shot Sentiment Analysis
    - Few-shot Learning
    - 리뷰 요약 생성
    - 반어법/은유 감지
    - Aspect 설명 생성
    """
    
    def __init__(self):
        self.client = llm_client
        self.cache = {}  # 간단한 캐시 (실제로는 Redis 사용)
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """
        LLM 기반 감성 분석 (Zero-shot)
        
        Returns:
            {
                "sentiment": "positive",
                "score": 0.8,
                "explanation": "..."
            }
        """
        if not settings.ENABLE_LLM or not self.client:
            return {"sentiment": "neutral", "score": 0.0, "explanation": "LLM disabled"}
        
        # 캐시 확인
        if settings.USE_LLM_CACHE and text in self.cache:
            return self.cache[text]
        
        prompt = f"""
다음 영화 리뷰의 감성을 분석해주세요.

리뷰: "{text}"

다음 형식으로 답변해주세요:
- 감성: positive/negative/neutral중 하나
- 점수: -1.0 (매우 부정) ~ 1.0 (매우 긍정)
- 설명: 왜 그렇게 판단했는지 1-2문장으로 설명

JSON 형식으로만 답변하세요.
"""
        
        try:
            if settings.LLM_PROVIDER == "openai":
                response = await self._call_openai(prompt)
            else:
                response = await self._call_anthropic(prompt)
            
            result = self._parse_llm_response(response)
            
            # 캐시 저장
            if settings.USE_LLM_CACHE:
                self.cache[text] = result
            
            return result
            
        except Exception as e:
            print(f"❌ LLM API error: {e}")
            return {"sentiment": "neutral", "score": 0.0, "explanation": f"Error: {str(e)}"}
    
    async def summarize_review(self, text: str, max_length: int = 100) -> str:
        """
        리뷰 요약 생성
        
        Args:
            text: 원본 리뷰
            max_length: 최대 길이 (글자 수)
            
        Returns:
            요약문 (3줄)
        """
        if not settings.ENABLE_LLM or not self.client:
            return text[:max_length] + "..."
        
        prompt = f"""
다음 영화 리뷰를 3줄로 요약해주세요.

리뷰: "{text}"

간결하고 핵심만 전달하는 요약을 작성하세요.
"""
        
        try:
            if settings.LLM_PROVIDER == "openai":
                response = await self._call_openai(prompt, max_tokens=150)
            else:
                response = await self._call_anthropic(prompt, max_tokens=150)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ LLM summarization error: {e}")
            return text[:max_length] + "..."
    
    async def generate_aspect_explanation(self, aspect: str, sentiment_score: float, text: str) -> str:
        """
        Aspect 분석 결과에 대한 자연어 설명 생성
        
        Args:
            aspect: "acting", "plot" 등
            sentiment_score: -1.0 ~ 1.0
            text: 원본 리뷰
            
        Returns:
            설명 문장
        """
        if not settings.ENABLE_LLM or not self.client:
            if sentiment_score > 0:
                return f"{aspect}에 대해 긍정적으로 평가했습니다."
            elif sentiment_score < 0:
                return f"{aspect}에 대해 부정적으로 평가했습니다."
            else:
                return f"{aspect}에 대한 언급이 없습니다."
        
        aspect_kr = {
            "acting": "연기",
            "plot": "스토리",
            "cinematography": "영상미",
            "soundtrack": "음악",
            "direction": "연출",
            "screenplay": "각본"
        }.get(aspect, aspect)
        
        prompt = f"""
다음 리뷰에서 '{aspect_kr}'에 대한 평가를 요약해주세요.

리뷰: "{text}"

감성 점수: {sentiment_score}

1-2문장으로 간결하게 설명하세요.
"""
        
        try:
            if settings.LLM_PROVIDER == "openai":
                response = await self._call_openai(prompt, max_tokens=80)
            else:
                response = await self._call_anthropic(prompt, max_tokens=80)
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ LLM explanation error: {e}")
            return f"{aspect_kr}에 대한 평가입니다."
    
    async def detect_sarcasm(self, text: str) -> Dict:
        """
        반어법/은유 감지
        
        Returns:
            {
                "is_sarcasm": bool,
                "confidence": float,
                "explanation": str
            }
        """
        if not settings.ENABLE_LLM or not self.client:
            return {"is_sarcasm": False, "confidence": 0.0, "explanation": "LLM disabled"}
        
        prompt = f"""
다음 리뷰에 반어법이나 은유가 사용되었는지 분석해주세요.

리뷰: "{text}"

JSON 형식으로 답변:
{{
    "is_sarcasm": true/false,
    "confidence": 0.0-1.0,
    "explanation": "..."
}}
"""
        
        try:
            if settings.LLM_PROVIDER == "openai":
                response = await self._call_openai(prompt)
            else:
                response = await self._call_anthropic(prompt)
            
            return self._parse_llm_response(response)
            
        except Exception as e:
            print(f"❌ LLM sarcasm detection error: {e}")
            return {"is_sarcasm": False, "confidence": 0.0, "explanation": f"Error: {str(e)}"}
    
    async def _call_openai(self, prompt: str, max_tokens: int = None) -> str:
        """OpenAI API 호출"""
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "당신은 영화 리뷰 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(self, prompt: str, max_tokens: int = None) -> str:
        """Anthropic Claude API 호출"""
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        response = await self.client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=settings.LLM_TEMPERATURE
        )
        
        return response.content[0].text
    
    def _parse_llm_response(self, response: str) -> Dict:
        """LLM 응답 파싱 (JSON)"""
        try:
            import json
            # JSON 블록 추출
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response and "}" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            return json.loads(json_str)
        except:
            # 파싱 실패 시 텍스트 그대로 반환
            return {"raw_response": response}


# 싱글톤 인스턴스
_llm_service = None


def get_llm_service() -> LLMService:
    """LLM 서비스 싱글톤"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
