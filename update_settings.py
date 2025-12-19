"""
설정 업데이트 스크립트
토글 UI에서 설정한 값을 .env.local에 자동으로 적용
"""

import sys
import os

def update_env_setting(key, value):
    """
    .env.local 파일의 설정 값을 업데이트
    """
    env_path = "backend/.env.local"
    
    # 파일 읽기
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # 해당 키 찾아서 업데이트
    updated = False
    new_lines = []
    
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            updated = True
        else:
            new_lines.append(line)
    
    # 키가 없으면 추가
    if not updated:
        new_lines.append(f"\n{key}={value}\n")
    
    # 파일 쓰기
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ {key}={value} 업데이트 완료")

def main():
    """
    명령줄 인자로 받은 설정 업데이트
    
    사용법:
    python update_settings.py ENABLE_LLM true
    python update_settings.py ENABLE_GPU false
    """
    if len(sys.argv) < 3:
        print("사용법: python update_settings.py <KEY> <VALUE>")
        print("예시: python update_settings.py ENABLE_LLM true")
        sys.exit(1)
    
    key = sys.argv[1]
    value = sys.argv[2]
    
    # 허용된 설정 키 목록
    allowed_keys = [
        "ENABLE_LLM",
        "ENABLE_GPU",
        "ENABLE_QUANTIZATION",
        "ENABLE_ABSA",
        "ENABLE_EMOTION_CLASSIFICATION",
        "ENABLE_GNN",
        "ENABLE_RL",
        "LLM_PROVIDER",
        "LLM_MODEL",
    ]
    
    if key not in allowed_keys:
        print(f"❌ 허용되지 않은 키: {key}")
        print(f"허용된 키: {', '.join(allowed_keys)}")
        sys.exit(1)
    
    update_env_setting(key, value)
    print("\n⚠️ 백엔드를 재시작해야 변경사항이 적용됩니다!")

if __name__ == "__main__":
    main()
