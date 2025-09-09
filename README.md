# 🦖 RAPTOR - Root Cause Analysis Platform

RAPTOR는 온톨로지 기반의 근본원인 분석 플랫폼입니다. 인과관계를 시각화하고 Claude AI를 통해 복합적인 문제의 근본원인을 분석합니다.

## 🚀 실행 방법

### 1. 의존성 설치

**Frontend (Vue.js)**
```bash
npm install
```

**Backend (FastAPI)**
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일에 Claude API 키를 설정하세요:
```env
# Claude API Configuration
CLAUDE_API_KEY=your-claude-api-key-here
```

### 3. 서버 실행

**FastAPI 백엔드 서버 (포트 8000)**
```bash
python server.py
```

**Vue.js 프론트엔드 (포트 3000)**
```bash
npm run dev
```

### 4. 접속

브라우저에서 http://localhost:3000 에 접속하세요.

## 🏗️ 아키텍처

```
┌─────────────────┐    HTTP    ┌─────────────────┐    HTTPS   ┌─────────────────┐
│   Vue.js        │──────────→│   FastAPI       │──────────→│   Claude API    │
│   Frontend      │            │   Backend       │            │   (Anthropic)   │
│   (Port 3000)   │            │   (Port 8000)   │            │                 │
└─────────────────┘            └─────────────────┘            └─────────────────┘
```

## 🔧 기술 스택

### Frontend
- **Vue 3** + **TypeScript** + **Composition API**
- **Tailwind CSS** - 스타일링
- **Vite** - 빌드 도구
- **vis-network** - 그래프 시각화
- **dayjs** - 시간 처리

### Backend
- **FastAPI** - API 서버
- **httpx** - HTTP 클라이언트
- **uvicorn** - ASGI 서버

## 📁 프로젝트 구조

```
raptor/
├── src/
│   ├── components/
│   │   ├── ChatPanel.vue      # 채팅 인터페이스
│   │   └── GraphPanel.vue     # 그래프 시각화
│   ├── services/
│   │   └── claude.ts          # Claude API 클라이언트
│   ├── types/
│   │   └── index.ts           # TypeScript 타입 정의
│   └── App.vue                # 메인 앱
├── server.py                  # FastAPI 백엔드
├── requirements.txt           # Python 의존성
└── package.json              # Node.js 의존성
```

## 💡 주요 기능

### 🔍 Ontology Visualization
- 인과관계 그래프 시각화
- 물리 시뮬레이션 효과
- 계층적 레이아웃 지원

### 🤖 Root Cause Analysis
- Claude AI 기반 대화형 분석
- 실시간 채팅 인터페이스
- 근본원인 분석에 특화된 프롬프트

## 🔒 보안

- API 키는 환경변수로 관리
- CORS 정책 적용
- FastAPI 프록시로 클라이언트에서 API 키 노출 방지

## 📝 개발 노트

### CORS 문제 해결
브라우저에서 직접 Claude API를 호출할 수 없기 때문에 FastAPI 백엔드를 프록시로 사용합니다.

### API 키 보안
- 클라이언트 코드에서 API 키가 노출되지 않도록 백엔드에서만 관리
- `.env` 파일은 `.gitignore`에 포함되어 버전관리에서 제외
