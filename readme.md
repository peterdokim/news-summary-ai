# ANS — AI 뉴스 요약기

키워드를 입력하면 네이버 또는 다음에서 뉴스를 자동으로 수집하고, AI가 비슷한 기사끼리 묶어 핵심 내용을 요약해주는 웹 서비스입니다.

---

## 주요 기능

- **뉴스 크롤링** — 네이버 뉴스 / 다음 뉴스에서 키워드 기반 기사 자동 수집
- **언론사 필터** — 경향신문, 조선일보, KBS, JTBC 등 18개 언론사 선택 가능
- **AI 클러스터링** — OpenAI 임베딩 + K-Means로 비슷한 기사끼리 자동 그룹화
- **AI 요약** — GPT-4o-mini로 각 그룹의 핵심 내용을 3문장 이내로 요약
- **실시간 진행 표시** — 크롤링 → 임베딩 → 클러스터링 → 요약 단계별 진행률 표시
- **검색 기록** — 이전 검색 결과를 로컬에 저장, 재검색 없이 즉시 확인 가능
- **접힘/펼침 사이드바** — 사이드바 토글로 화면 공간 조절 가능

---

## 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| 프론트엔드 | Next.js 16, React 18, Tailwind CSS v3 |
| 백엔드 | Python, Flask, Gunicorn |
| AI | OpenAI API (text-embedding-3-small, GPT-4o-mini) |
| 크롤링 | requests, BeautifulSoup4 |
| 클러스터링 | scikit-learn (K-Means) |
| 배포 | Vercel (프론트엔드), Render (백엔드) |

---

## 프로젝트 구조

```
news-summary-ai/
├── pages/
│   ├── index.js          # 검색 페이지 (메인)
│   ├── news.js           # 결과 페이지
│   └── api/
│       ├── search.js     # 검색 요청 → 백엔드 연결
│       └── progress.js   # 진행률 폴링
├── api/
│   ├── news_summarizer.py  # 크롤링 / 임베딩 / 클러스터링 / 요약 핵심 로직
│   └── config.py           # 언론사 목록 (PRESS_LIST)
├── server.py             # Flask 서버 (백그라운드 작업 관리)
├── requirements.txt      # Python 패키지 목록
├── package.json          # Node 패키지 목록
└── .env                  # 환경변수 (절대 커밋 금지)
```

---

## 로컬 실행 방법

### 1. 환경변수 설정

프로젝트 루트에 `.env` 파일 생성:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 2. Python 백엔드 실행

```bash
pip install -r requirements.txt
python server.py
```

Flask 서버가 `http://localhost:5000` 에서 실행됩니다.

### 3. Next.js 프론트엔드 실행

```bash
npm install
npm run dev
```

브라우저에서 `http://localhost:3000` 접속.

---

## 배포 구조

```
사용자 브라우저
     │
     ▼
Vercel (Next.js)          ← 프론트엔드
     │  /api/search.js
     │  /api/progress.js
     ▼
Render (Flask)            ← 백엔드
     │  POST /api/summarize-start
     │  GET  /api/progress/<job_id>
     ▼
OpenAI API
```

### Vercel 환경변수 설정

Vercel 프로젝트 설정 → Environment Variables:

```
PYTHON_API_URL=https://your-app.onrender.com
```

### Render 환경변수 설정

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/summarize-start` | 백그라운드 요약 작업 시작, job_id 반환 |
| GET | `/api/progress/<job_id>` | 진행률 및 결과 조회 |
| POST | `/api/summarize` | 동기식 요약 (구버전 호환) |
| GET | `/api/health` | 서버 상태 확인 |

---

## 사용 방법

1. 검색창에 키워드 입력 (예: `반도체`, `AI`, `부동산`)
2. 검색 엔진 선택 — 네이버 / 다음
3. 원하는 언론사 선택 (선택 사항)
4. **검색** 버튼 클릭
5. 진행률 표시줄이 단계별로 업데이트됨
6. 완료 후 뉴스 그룹 목록과 AI 요약 확인
7. 사이드바의 최근 검색 목록을 클릭하면 이전 결과를 즉시 확인 가능

---

## 지원 언론사

경향신문, 국민일보, 동아일보, 매일경제, 시사IN, 연합뉴스, 조선일보, 중앙일보, 한겨레, 한국경제, 한국일보, KBS, JTBC, MBC, OSEN, SBS, TV조선, YTN

---

## 자주 발생하는 문제

**"Flask 서버에 연결할 수 없습니다"**
- `python server.py` 가 실행 중인지 확인
- `.env` 의 `PYTHON_API_URL` 확인

**"OPENAI_API_KEY가 설정되지 않았습니다"**
- 프로젝트 루트에 `.env` 파일이 있는지 확인
- API 키가 `sk-` 또는 `sk-proj-` 로 시작하는지 확인

**검색 결과가 없음**
- 다른 키워드로 시도
- 검색 엔진을 네이버 ↔ 다음으로 변경
- 기사 수를 늘려서 재시도

**Render 배포 후 첫 검색이 느림**
- Render 무료 플랜은 15분 비활성 시 서버가 종료됩니다
- [UptimeRobot](https://uptimerobot.com) 에서 `/api/health` 를 5분마다 핑하도록 설정하면 해결됩니다

---

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요.
- OpenAI API 키가 노출된 경우 [플랫폼](https://platform.openai.com/api-keys) 에서 즉시 폐기하고 새 키를 발급하세요.
- 
