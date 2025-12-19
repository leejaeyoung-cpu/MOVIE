"""
시스템 설정 API 라우터
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path

router = APIRouter()

# 설정 파일 경로
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


class SystemConfig(BaseModel):
    """시스템 설정 모델"""
    enable_llm: bool = True
    enable_gpu: bool = False
    enable_quantization: bool = False
    enable_absa: bool = True
    enable_emotion_classification: bool = True
    enable_gnn: bool = False


def load_config() -> SystemConfig:
    """설정 파일 로드"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return SystemConfig(**data)
    else:
        # 기본 설정 반환
        return SystemConfig()


def save_config(config: SystemConfig):
    """설정 파일 저장"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config.dict(), f, indent=2, ensure_ascii=False)


@router.get("/config", response_model=SystemConfig)
async def get_config():
    """
    현재 시스템 설정 조회
    """
    return load_config()


@router.put("/config", response_model=SystemConfig)
async def update_config(config: SystemConfig):
    """
    시스템 설정 업데이트
    
    **Parameters:**
    - enable_llm: LLM 기능 활성화 여부
    - enable_gpu: GPU 사용 여부
    - enable_quantization: 모델 양자화 사용 여부
    - enable_absa: ABSA 기능 활성화 여부
    - enable_emotion_classification: 감정 분류 활성화 여부
    - enable_gnn: GNN 기능 활성화 여부
    """
    try:
        save_config(config)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 저장 실패: {str(e)}")


@router.post("/config/reset")
async def reset_config():
    """
    설정을 기본값으로 리셋
    """
    default_config = SystemConfig()
    save_config(default_config)
    return {"message": "설정이 기본값으로 초기화되었습니다", "config": default_config}
