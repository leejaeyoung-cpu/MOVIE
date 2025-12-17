# 🚀 GitHub에 프로젝트 업로드하기

## 📋 준비사항

1. Git이 설치되어 있어야 합니다
   ```bash
   # Git 설치 확인
   git --version
   ```

2. GitHub 계정 및 리포지토리
   - 리포지토리 URL: https://github.com/leejaeyoung-cpu/MOVIE

---

## 🎯 Step-by-Step 가이드

### Step 1: .gitignore 파일 생성

프로젝트 루트에 `.gitignore` 파일이 필요합니다.

```bash
# 미션18 폴더에서 실행
cd c:/Users/brook/Desktop/미션18
```

`.gitignore` 파일 내용:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# 환경 변수
.env
*.env

# 데이터베이스
*.db
*.sqlite
*.sqlite3

# ML 모델 (너무 크면 Git LFS 사용)
*.pt
*.pth
*.onnx
*.pkl
models/
!models/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# 임시 파일
tmp/
temp/
```

---

### Step 2: Git 초기화

```bash
# 미션18 폴더에서
git init
```

---

### Step 3: 원격 저장소 연결

```bash
git remote add origin https://github.com/leejaeyoung-cpu/MOVIE.git
```

---

### Step 4: 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋
git commit -m "🎬 Initial commit: Netflix-grade Movie Review & AI Recommendation System

Features:
- Multi-Model Ensemble Sentiment Analysis (KoBERT + RoBERTa + ELECTRA)
- Aspect-Based Sentiment Analysis (6 aspects)
- Multi-Emotion Classification (6 emotions)
- Neural Collaborative Filtering (NCF)
- Graph Neural Networks (GNN)
- Sequential Recommendation (Transformer/GRU/LSTM)
- Reinforcement Learning (Contextual Bandit)
- LLM Integration (GPT-4/Claude)
- GPU/CPU toggle, INT8 Quantization
- FastAPI Backend + Streamlit Frontend
"
```

---

### Step 5: GitHub에 Push

```bash
# main 브랜치로 푸시
git branch -M main
git push -u origin main
```

---

## 📝 이후 커밋 방법

파일을 수정한 후:

```bash
# 변경사항 확인
git status

# 변경된 파일 추가
git add .

# 커밋
git commit -m "Update: [변경 내용 설명]"

# Push
git push
```

---

## 🔑 GitHub 인증 (처음 한번만)

### 방법 1: Personal Access Token (추천)

1. GitHub 웹사이트 접속
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token" 클릭
4. 권한 선택: `repo` 전체 선택
5. 토큰 생성 후 복사 (⚠️ 다시 볼 수 없으니 안전한 곳에 저장)
6. Git push 시 비밀번호 대신 이 토큰 입력

### 방법 2: SSH Key

```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"

# 공개 키 복사
cat ~/.ssh/id_ed25519.pub

# GitHub Settings → SSH and GPG keys → New SSH key에 붙여넣기

# 원격 저장소 URL 변경
git remote set-url origin git@github.com:leejaeyoung-cpu/MOVIE.git
```

---

## 📊 대용량 모델 파일 처리

ML 모델 파일이 100MB 이상이면 Git LFS 사용:

```bash
# Git LFS 설치
git lfs install

# 추적할 파일 형식 지정
git lfs track "*.pt"
git lfs track "*.pth"
git lfs track "*.onnx"

# .gitattributes 파일 추가
git add .gitattributes

# 커밋 및 푸시
git add .
git commit -m "Add large model files with Git LFS"
git push
```

---

## 🎨 README.md 업데이트

GitHub 리포지토리 메인 페이지에 표시될 README를 업데이트하세요.

현재 `README.md` 파일이 이미 생성되어 있습니다:
- 프로젝트 설명
- 기능 목록
- 설치 방법
- 사용법
- API 문서
- 스크린샷 (배포 후 추가)

---

## 🌐 GitHub Pages로 문서 배포 (선택사항)

API 문서를 GitHub Pages로 배포:

```bash
# docs 브랜치 생성
git checkout -b gh-pages

# index.html 생성 (FastAPI docs redirect)
echo '<meta http-equiv="refresh" content="0; url=https://your-api-url.railway.app/docs">' > index.html

git add index.html
git commit -m "Add GitHub Pages"
git push origin gh-pages

# main 브랜치로 돌아가기
git checkout main
```

Settings → Pages → Source: gh-pages 선택

---

## 🔗 추가 링크

프로젝트를 더욱 전문적으로 만들기:

1. **Badges 추가** (README.md 상단)
```markdown
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
```

2. **GitHub Actions CI/CD**
`.github/workflows/python-app.yml` 생성:
```yaml
name: Python Application

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
    - name: Run tests
      run: |
        pytest backend/tests/
```

3. **License 추가**
`LICENSE` 파일 생성 (MIT License):
```
MIT License

Copyright (c) 2024 이재영

Permission is hereby granted, free of charge...
```

---

## ✅ 완료 체크리스트

- [ ] `.gitignore` 파일 생성
- [ ] Git 초기화 (`git init`)
- [ ] 원격 저장소 연결
- [ ] 첫 커밋 및 푸시
- [ ] README.md 확인
- [ ] 스크린샷 추가 (배포 후)
- [ ] LICENSE 파일 추가
- [ ] GitHub Actions 설정 (선택)

---

**🎉 완료 후 확인:**
https://github.com/leejaeyoung-cpu/MOVIE

프로젝트가 GitHub에 성공적으로 업로드되었습니다!
