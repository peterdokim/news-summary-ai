# Archive

더 이상 사용하지 않는 초기 버전 파일들입니다.

## 파일 목록

### news_summarizer.py
- **사용 기술**: Selenium 크롤링 + HuggingFace `gogamza/kobart-summarization`
- **변경 사유**: Selenium → BeautifulSoup로 전환, KoBART → OpenAI API로 변경
- **대체 파일**: 현재 버전의 뉴스 요약 기능

### web_crawling.ipynb
- **사용 기술**: Selenium 기반 웹 크롤링
- **변경 사유**: BeautifulSoup로 크롤링 방식 변경
- **대체 파일**: 현재 버전의 크롤링 모듈

## 기술 스택 변경 이력
- 크롤링: Selenium → **BeautifulSoup**
- 요약 모델: HuggingFace KoBART → **OpenAI API**