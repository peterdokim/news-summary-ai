# 뉴스 요약 봇 (News Summary AI)

## 프로젝트 개요
한국 뉴스 포털(네이버, 다음)에서 뉴스를 크롤링하고, AI 기반 임베딩 → 클러스터링 → 요약 파이프라인으로 자동 요약하는 웹 애플리케이션.
최종적으로 사용자가 웹사이트에서 키워드와 언론사를 선택해 요약된 뉴스를 볼 수 있는 서비스를 목표로 함.

## 기술 스택
- **백엔드**: Python 3.11 (BeautifulSoup, requests)
- **AI/ML**: OpenAI API (text-embedding 모델, GPT-4o-mini), scikit-learn (K-Means 클러스터링)
- **프론트엔드**: Next.js
- **버전 관리**: Git + GitHub
- **환경**: macOS (Apple Silicon), VS Code
- **환경변수**: `.env` 파일에 `OPENAI_API_KEY` 저장, `python-dotenv`로 로드

## 프로젝트 구조
```
news-summary-ai/
├── news_summarizer.py    # 메인 파이프라인 (NewsSummarizer 클래스)
├── config.py             # 언론사 목록 (PRESS_LIST) 설정
├── .env                  # OpenAI API 키 (gitignore 대상)
├── .gitignore
├── package.json          # Next.js 프론트엔드
├── package-lock.json
└── (Next.js 관련 파일들)
```

## 핵심 파이프라인 (news_summarizer.py)
`NewsSummarizer` 클래스가 전체 흐름을 관리:

1. **`get_news_url()`** → 네이버/다음에서 뉴스 URL 수집
   - `_get_naver_news_urls()`: 네이버 뉴스 검색. `service_area=1`로 네이버 뉴스 제휴사만 필터. 페이지네이션 지원 (10개씩 `start` 파라미터)
   - `_get_daum_news_urls()`: 다음 뉴스 검색
2. **`extract_news_article()`** → BeautifulSoup으로 기사 본문 추출
3. **`get_embeddings()`** → OpenAI 임베딩 API로 텍스트 벡터화 (지수 백오프 재시도 로직 포함)
4. **`cluster_articles()`** → K-Means로 유사 기사 그룹화
5. **`summarize_cluster()`** → GPT-4o-mini로 각 클러스터의 대표 기사 요약
6. **`run()`** → 위 단계를 순서대로 실행하는 메인 메서드

## 언론사 필터 시스템 (config.py)
`PRESS_LIST` 딕셔너리로 18개 언론사를 통합 관리:

```python
# 구조: "번호": ("표시이름", "네이버코드", "다음cp코드")
PRESS_LIST = {
    "1": ("경향신문", "1032", "16akMkKFDu6n8GTzZr"),
    "2": ("국민일보", "1005", "16tZcm4AixcQK6HoII"),
    # ... 가나다순 정렬, 총 18개
}
```

- **네이버**: URL 파라미터 `mynews=1&news_office_checked={네이버코드}` 로 필터
- **다음**: URL 파라미터 `cp={다음cp코드}&cpname={언론사이름}` + `DA=STC`로 필터
- 다음의 cp코드는 JavaScript 동적 로딩이라 requests로 파싱 불가 → 수동으로 18개 추출해서 하드코딩함

## 커스텀 예외 클래스
```
NewsSearchError       # 뉴스 검색 실패
ArticleExtractionError # 기사 본문 추출 실패
EmbeddingError        # 임베딩 생성 실패
ClusteringError       # 클러스터링 실패
SummarizationError    # 요약 생성 실패
```

## 알려진 제한사항 / 주의사항
- `m.sports.naver.com`, `m.entertain.naver.com`은 CSR이라 requests로 본문 추출 불가 → `n.news.naver.com` 도메인만 안정적
- 다음 언론사 필터의 `cp=` 코드는 문서화되어 있지 않음. 브라우저 개발자 도구의 `data-code` 속성에서 수동 추출
- 네이버 `service_area=1` (네이버뉴스만)과 `service_area=0` (전체)의 차이 주의
- 페이지네이션: 네이버는 `start` 파라미터로 10개씩 batch

## Git 브랜치
- `feature/news-summarizer` 브랜치에서 작업 중
- `.gitignore`에 포함해야 하는 것들: `node_modules/`, `.next/`, `.env`, `__pycache__/`

## 완료된 작업
- [x] 기본 크롤링/요약 파이프라인 (NewsSummarizer 클래스)
- [x] Selenium → BeautifulSoup 마이그레이션
- [x] HuggingFace → OpenAI API 전환
- [x] 커스텀 예외 클래스 + 에러 핸들링 (지수 백오프 재시도)
- [x] 네이버 페이지네이션 (10개씩 복수 페이지 수집, 중복 필터링)
- [x] 네이버/다음 통합 언론사 필터 (PRESS_LIST로 통합 관리)
- [x] 다음 cp코드 18개 수동 추출 및 하드코딩
- [x] config.py 분리 (설정과 로직 분리)
- [x] press_choice 단일 파라미터 시스템 (press_code, press_name 대신)
- [x] Git 워크플로우 세팅 (.gitignore, 브랜치 관리)
- [x] Next.js 프론트엔드 초기 세팅

## 진행 중 / TODO
- [ ] 프론트엔드 웹 UI 구현 (Next.js)
  - 키워드 입력, 검색 엔진 선택, 언론사 별표/필터 기능
- [ ] 백엔드 API 엔드포인트 구현 (프론트엔드 연동용)
- [ ] 다양한 뉴스 콘텐츠 타입 핸들링 (스포츠/연예 등 CSR 페이지)
- [ ] 배포 전략 수립
- [ ] API 비용 최적화

## 코딩 스타일
- 한국어 주석/docstring 사용
- 커밋 메시지: `feat:`, `fix:` 등 conventional commits 스타일
- 로깅: Python `logging` 모듈 사용 (`logger.info`, `logger.warning` 등)
- 타입 힌트 사용 (`List[Dict]`, `Optional[str]` 등)