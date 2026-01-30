import os
import requests
import urllib.parse
import numpy as np
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances
import logging
from config import PRESS_LIST

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class NewsSearchError(Exception):
    """뉴스 검색 관련 예외"""
    pass


class ArticleExtractionError(Exception):
    """기사 추출 관련 예외"""
    pass


class EmbeddingError(Exception):
    """임베딩 생성 관련 예외"""
    pass


class ClusteringError(Exception):
    """클러스터링 관련 예외"""
    pass


class SummarizationError(Exception):
    """요약 생성 관련 예외"""
    pass


class NewsSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        NewsSummarizer 초기화
        
        Args:
            api_key: OpenAI API 키 (없으면 환경변수에서 로드)
            
        Raises:
            ValueError: API 키가 없거나 유효하지 않은 경우
        """
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/143.0.0.0 Safari/537.36"
            )
        }

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다.\n"
                "1. .env 파일을 만들고 OPENAI_API_KEY=sk-xxx 형식으로 저장하세요.\n"
                "2. 또는 환경변수로 설정하세요: export OPENAI_API_KEY=sk-xxx\n"
                "3. 또는 생성자에 api_key 파라미터로 전달하세요."
            )
        
        if not self.api_key.startswith(('sk-', 'sk-proj-')):
            logger.warning("API 키 형식이 일반적이지 않습니다. 확인해 주세요.")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"OpenAI 클라이언트 초기화 실패: {e}")

    def get_news_url(
        self, 
        keyword: str, 
        search_engine: str, 
        max_articles: int,
        press_choice: str = None
    ) -> List[str]:
        """
        검색 엔진에서 뉴스 URL 수집
        
        Args:
            keyword: 검색 키워드
            search_engine: 검색 엔진 ('네이버' 또는 '다음')
            max_articles: 최대 기사 수
            press_choice: PRESS_LIST 딕셔너리 키 (예: "1"=경향신문)
                          None이면 전체 언론사 검색
            
        Returns:
            뉴스 URL 리스트
            
        Raises:
            ValueError: 지원하지 않는 검색 엔진인 경우
            NewsSearchError: 검색 중 오류 발생 시
        """
        supported_engines = {'네이버', '다음'}
        
        if not keyword or not keyword.strip():
            raise ValueError("검색 키워드가 비어있습니다.")
        
        if search_engine not in supported_engines:
            raise ValueError(
                f"지원하지 않는 검색엔진입니다: {search_engine}. "
                f"지원 엔진: {', '.join(supported_engines)}"
            )
        
        if max_articles < 1:
            raise ValueError("max_articles는 1 이상이어야 합니다.")
        
        encoded = urllib.parse.quote(keyword.strip())
        
        try:
            press_code = None
            press_name = None
            cp = None
            
            if press_choice:
                press_name, press_code, cp = PRESS_LIST[press_choice]
            
            if search_engine == "네이버":
                return self._get_naver_news_urls(encoded, max_articles, press_code)
            elif search_engine == "다음":
                return self._get_daum_news_urls(encoded, max_articles, press_name, cp)
        except requests.RequestException as e:
            raise NewsSearchError(f"뉴스 검색 중 네트워크 오류: {e}")
        except Exception as e:
            raise NewsSearchError(f"뉴스 검색 중 오류 발생: {e}")
        
    def _get_naver_news_urls(
        self, 
        encoded_keyword: str, 
        max_articles: int,
        press_code: str = None
    ) -> List[str]:
        """네이버 뉴스 검색에서 기사 URL 수집 (페이지네이션 지원)"""
        
        news_urls = []
        start = 1
        
        while len(news_urls) < max_articles:
            # 언론사 필터가 있으면 새 URL 형식 사용
            if press_code:
                base_url = (
                    f"https://search.naver.com/search.naver?"
                    f"ssc=tab.news.all&query={encoded_keyword}&start={start}"
                    f"&sm=tab_opt&sort=0&mynews=1&office_type=2"
                    f"&office_section_code=1&news_office_checked={press_code}&service_area=0"
                )
            else:
                base_url = (
                    f"https://search.naver.com/search.naver?where=news"
                    f"&query={encoded_keyword}&start={start}"
                    f"&sm=tab_opt&sort=0&pd=-1&ds=&de=&service_area=1"
                )
            
            resp = requests.get(base_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            
            domains = [
                "news.naver.com",
                "m.entertain.naver.com",
                "m.sports.naver.com"
            ]
            
            found_in_page = 0
            for span in soup.select(
                "span.sds-comps-text.sds-comps-text-ellipsis.sds-comps-text-ellipsis-1"
            ):
                text = span.get_text(strip=True)
                if text != "네이버뉴스":
                    continue

                a_tag = span.find_parent("a")
                if not a_tag:
                    continue

                href = a_tag.get("href")
                if not href:
                    continue

                if any(domain in href for domain in domains):
                    if href not in news_urls:
                        news_urls.append(href)
                        found_in_page += 1

                    if len(news_urls) >= max_articles:
                        break
            
            # 더 이상 기사가 없으면 종료
            if found_in_page == 0:
                break
                
            start += 10  # 다음 페이지
        
        if not news_urls:
            logger.warning("네이버에서 뉴스를 찾지 못했습니다.")
            
        return news_urls
    
    def _get_daum_news_urls(
        self, 
        encoded_keyword: str, 
        max_articles: int,
        press_name: str = None,
        cp: str = None
    ) -> List[str]:
        """다음 뉴스 URL 수집"""
        if press_name and cp:
            encoded_press = urllib.parse.quote(press_name)
            base_url = (
                f"https://search.daum.net/search?"
                f"w=news&DA=STC&cluster=y&q={encoded_keyword}"
                f"&cp={cp}&cpname={encoded_press}"
            )
        else:
            base_url = (
                f"https://search.daum.net/search?"
                f"nil_suggest=btn&w=news&DA=SBC&cluster=y&q={encoded_keyword}"
            )
        print(f"[DEBUG] press_name: {press_name}")
        print(f"[DEBUG] base_url: {base_url}")
        news_urls = []
        page = 1
        max_pages = 10  # 무한 루프 방지
        
        while len(news_urls) < max_articles and page <= max_pages:
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}&p={page}"
            
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as e:
                logger.warning(f"다음 뉴스 페이지 {page} 요청 실패: {e}")
                break
                
            soup = BeautifulSoup(resp.text, "html.parser")
            
            found_in_page = 0
            for a_tag in soup.select("strong.tit-g.clamp-g > a[href]"):
                href = a_tag.get("href", "")
                
                if not href:
                    continue
                
                if href not in news_urls:
                    news_urls.append(href)
                    found_in_page += 1
                
                if len(news_urls) >= max_articles:
                    break
            
            if found_in_page == 0:
                break
            
            page += 1
        
        if not news_urls:
            logger.warning(f"다음에서 뉴스를 찾지 못했습니다.")
            
        return news_urls
         
    def extract_news_article(self, url: str) -> Dict[str, str]:
        """
        BeautifulSoup을 사용하여 기사 텍스트 추출
        
        Args:
            url: 기사 URL
            
        Returns:
            기사 정보 딕셔너리
        """
        if not url or not url.strip():
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': 'URL이 비어있습니다.',
            }
            
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 제목 추출
            title_elem = (
                soup.select_one("#title_area") or
                soup.select_one('h2.ArticleHead_article_title__qh8GV') or
                soup.select_one('h3.tit_view')
            )
        
            title = title_elem.get_text(strip=True) if title_elem else None

            # 본문 추출
            article = (
                soup.select_one("#dic_area") or
                soup.select_one("div._article_content") or
                soup.select_one("section[dmcf-sid]")
            )
            text = None

            if article:
                for tag in article.find_all(['img', 'script', 'style', 'iframe']):
                    tag.decompose()
                        
                text = article.get_text(separator=' ', strip=True)
                text = ' '.join(text.split())

            if not title and not text:
                return {
                    'url': url,
                    'title': None,
                    'text': None,
                    'success': False,
                    'error': '제목과 본문을 찾을 수 없습니다.',
                }
                    
            return {
                'url': url,
                'title': title,
                'text': text,
                'success': True,
            }
        
        except requests.Timeout:
            logger.warning(f"기사 요청 타임아웃: {url}")
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': '요청 타임아웃 (15초 초과)',
            }
        except requests.HTTPError as e:
            logger.warning(f"HTTP 오류 ({e.response.status_code}): {url}")
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': f'HTTP 오류: {e.response.status_code}',
            }
        except requests.RequestException as e:
            logger.warning(f"요청 실패: {url} - {e}")
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': f'요청 실패: {str(e)}',
            }
        except Exception as e:
            logger.error(f"파싱 실패: {url} - {e}")
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': f'파싱 실패: {str(e)}',
            }
        
    def crawl_news(
        self, 
        keyword: str, 
        search_engine: str, 
        max_articles: int = 5,
        press_choice: str = None
    ) -> List[Dict[str, str]]:
        """
        키워드로 뉴스 검색 → 모든 기사 본문 추출
        
        Args:
            keyword: 검색 키워드
            search_engine: 검색 엔진 (포털 사이트)
            max_articles: 최대 기사 수
            press_choice: PRESS_LIST 딕셔너리 키 (예: "1"=경향신문)
                          None이면 전체 언론사 검색
        
        Returns:
            기사 정보 리스트 (제목, 본문, URL 등)
        """
        urls = self.get_news_url(keyword, search_engine, max_articles, press_choice)
        
        if not urls:
            logger.info(f"'{keyword}'에 대한 뉴스 URL을 찾지 못했습니다.")
            return []

        articles = []
        success_count = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"기사 추출 중... ({i}/{len(urls)})")
            result = self.extract_news_article(url)
            articles.append(result)
            
            if result['success']:
                success_count += 1

        logger.info(f"기사 추출 완료: {success_count}/{len(urls)} 성공")
        return articles

    def prepare_articles_for_embedding(
        self, 
        articles: List[Dict]
    ) -> Tuple[List[Dict], List[str]]:
        """
        크롤링 결과에서 성공한 기사만 추출하고 임베딩용 텍스트 준비

        Args:
            articles: 크롤링 결과 (기사 정보 리스트)

        Returns:
            (valid_articles, texts_for_embedding)
        """
        if not articles:
            return [], []
            
        valid_articles = []
        texts_for_embedding = []

        for article in articles:
            if not article.get('success'):
                continue
            if not article.get('text'):
                continue

            valid_articles.append(article)

            title = article.get('title') or ''
            text = article.get('text') or ''

            combined = f"[제목] {title}\n\n[본문] {text[:1500]}"
            texts_for_embedding.append(combined)
        
        return valid_articles, texts_for_embedding
        
    def get_embeddings(
        self, 
        texts: List[str], 
        max_retries: int = 3
    ) -> np.ndarray:
        """
        기사 텍스트 리스트를 벡터로 변환

        Args:
            texts: 변환할 텍스트 리스트
            max_retries: 최대 재시도 횟수

        Returns:
            numpy 배열 (texts 개수 x 1536 차원)
            
        Raises:
            EmbeddingError: 임베딩 생성 실패 시
        """
        if not texts:
            raise EmbeddingError("임베딩할 텍스트가 없습니다.")

        # 빈 텍스트 처리
        texts = [t.strip() if t and t.strip() else " " for t in texts]

        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )

                embeddings = [item.embedding for item in response.data]
                return np.array(embeddings)
                
            except RateLimitError as e:
                last_error = e
                wait_time = 2 ** attempt  # 지수 백오프
                logger.warning(
                    f"Rate limit 도달. {wait_time}초 후 재시도... "
                    f"({attempt + 1}/{max_retries})"
                )
                import time
                time.sleep(wait_time)
                
            except APIConnectionError as e:
                last_error = e
                logger.warning(
                    f"API 연결 오류. 재시도 중... ({attempt + 1}/{max_retries})"
                )
                import time
                time.sleep(1)
                
            except APIError as e:
                last_error = e
                logger.error(f"OpenAI API 오류: {e}")
                break  # API 오류는 재시도해도 의미 없음
                
            except Exception as e:
                last_error = e
                logger.error(f"임베딩 생성 중 예상치 못한 오류: {e}")
                break
        
        raise EmbeddingError(f"임베딩 생성 실패: {last_error}")
    
    def cluster_articles(
        self, 
        embeddings: np.ndarray, 
        articles: List[Dict],
        n_clusters: int = 3
    ) -> List[Dict]:
        """
        임베딩 벡터를 기반으로 기사들을 클러스터링

        Args:
            embeddings: 임베딩 벡터 배열 (기사 수 x 1536)
            articles: 기사 정보 리스트
            n_clusters: 클러스터 개수

        Returns:
            클러스터별 기사 정보 리스트
            
        Raises:
            ClusteringError: 클러스터링 실패 시
        """
        if len(articles) == 0:
            raise ClusteringError("클러스터링할 기사가 없습니다.")
            
        if len(embeddings) != len(articles):
            raise ClusteringError(
                f"임베딩 수({len(embeddings)})와 "
                f"기사 수({len(articles)})가 일치하지 않습니다."
            )
        
        if n_clusters < 1:
            raise ClusteringError("클러스터 수는 1 이상이어야 합니다.")
            
        # 기사 수에 맞게 클러스터 수 조정
        actual_clusters = min(n_clusters, len(articles))
        
        if actual_clusters != n_clusters:
            logger.info(
                f"기사 수가 적어 클러스터 수를 {n_clusters}에서 "
                f"{actual_clusters}로 조정합니다."
            )
        
        try:
            kmeans = KMeans(
                n_clusters=actual_clusters, 
                random_state=42, 
                n_init=10
            )
            labels = kmeans.fit_predict(embeddings)
        except Exception as e:
            raise ClusteringError(f"K-Means 클러스터링 실패: {e}")
        
        clusters = []
        for cluster_id in range(actual_clusters):
            indices = np.where(labels == cluster_id)[0]
            
            if len(indices) == 0:
                continue
            
            cluster_articles = [articles[i] for i in indices]
            cluster_embeddings = embeddings[indices]
            
            centroid = kmeans.cluster_centers_[cluster_id]
            distances = cosine_distances([centroid], cluster_embeddings)[0]
            representative_idx = np.argmin(distances)
            representative = cluster_articles[representative_idx]
            
            clusters.append({
                'cluster_id': cluster_id,
                'articles': cluster_articles,
                'representative': representative,
                'size': len(cluster_articles)
            })
        
        # 클러스터 크기순 정렬 (큰 것부터)
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        # cluster_id 재할당
        for i, cluster in enumerate(clusters):
            cluster['cluster_id'] = i
            
        return clusters
    
    def summarize_cluster(
        self, 
        cluster: Dict, 
        max_retries: int = 3
    ) -> Dict:
        """
        클러스터의 대표 기사 요약 + 관련 기사 제목 리스트
        
        Args:
            cluster: 클러스터 정보
            max_retries: 최대 재시도 횟수
        
        Returns:
            요약 결과 딕셔너리
            
        Raises:
            SummarizationError: 요약 생성 실패 시
        """
        representative = cluster.get('representative', {})
        text = representative.get('text', '')
        
        summary = "요약할 내용이 없습니다."
        
        if text and text.strip():
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "뉴스 기사를 3문장 이내로 핵심만 요약해주세요. "
                                    "한국어로 답변하세요."
                                )
                            },
                            {
                                "role": "user",
                                "content": text[:4000]  # 토큰 제한 고려
                            }
                        ],
                        max_tokens=300,
                        temperature=0.3
                    )
                    summary = response.choices[0].message.content
                    break
                    
                except RateLimitError as e:
                    last_error = e
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Rate limit 도달. {wait_time}초 후 재시도... "
                        f"({attempt + 1}/{max_retries})"
                    )
                    import time
                    time.sleep(wait_time)
                    
                except APIConnectionError as e:
                    last_error = e
                    logger.warning(
                        f"API 연결 오류. 재시도 중... ({attempt + 1}/{max_retries})"
                    )
                    import time
                    time.sleep(1)
                    
                except APIError as e:
                    last_error = e
                    logger.error(f"OpenAI API 오류: {e}")
                    summary = f"요약 생성 실패: API 오류"
                    break
                    
                except Exception as e:
                    last_error = e
                    logger.error(f"요약 생성 중 예상치 못한 오류: {e}")
                    summary = f"요약 생성 실패: {str(e)}"
                    break
            else:
                # 모든 재시도 실패
                summary = f"요약 생성 실패 (재시도 {max_retries}회 초과)"
        
        # 관련 기사 제목 리스트 (대표 기사 제외)
        rep_title = representative.get('title')
        related_titles = [
            article.get('title') 
            for article in cluster.get('articles', []) 
            if article.get('title') and article.get('title') != rep_title
        ]
        
        return {
            'cluster_id': cluster.get('cluster_id', 0),
            'size': cluster.get('size', 0),
            'summary': summary,
            'representative_title': rep_title or '제목 없음',
            'representative_url': representative.get('url', ''),
            'related_titles': related_titles
        }

    def summarize_all_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """
        모든 클러스터 요약
        
        Args:
            clusters: 클러스터 리스트
            
        Returns:
            요약 결과 리스트
        """
        if not clusters:
            logger.warning("요약할 클러스터가 없습니다.")
            return []
            
        results = []
        for i, cluster in enumerate(clusters, 1):
            logger.info(f"클러스터 요약 중... ({i}/{len(clusters)})")
            result = self.summarize_cluster(cluster)
            results.append(result)
            
        return results
    
    def run(
        self, 
        keyword: str, 
        search_engine: str, 
        max_articles: int = 20, 
        n_clusters: int = 3,
        press_choice: str = None
    ) -> List[Dict]:
        """
        전체 파이프라인 실행: 크롤링 -> 임베딩 -> 클러스터링 -> 요약

        Args:
            keyword: 검색 키워드
            search_engine: 검색 엔진 (포털 사이트)
            max_articles: 최대 크롤링 기사 수
            n_clusters: 클러스터 개수
            press_choice: PRESS_LIST 딕셔너리 키 (예: "1"=경향신문)
                          None이면 전체 언론사 검색

        Returns:
            클러스터별 요약 결과 리스트
            
        Raises:
            ValueError: 입력값이 유효하지 않은 경우
            NewsSearchError: 뉴스 검색 실패 시
            EmbeddingError: 임베딩 생성 실패 시
            ClusteringError: 클러스터링 실패 시
        """
        logger.info(f"=== 뉴스 요약 시작: '{keyword}' ({search_engine}) ===")
        
        # 1. 크롤링
        logger.info("1단계: 뉴스 크롤링...")
        try:
            articles = self.crawl_news(keyword, search_engine, max_articles, press_choice)
        except NewsSearchError as e:
            logger.error(f"크롤링 실패: {e}")
            raise
        
        # 2. 유효한 기사 필터링
        logger.info("2단계: 기사 데이터 준비...")
        valid_articles, texts = self.prepare_articles_for_embedding(articles)
        
        if len(valid_articles) == 0:
            logger.warning(f"'{keyword}'에 대한 유효한 뉴스 기사가 없습니다.")
            return []
        
        logger.info(f"유효한 기사: {len(valid_articles)}개")
        
        # 3. 임베딩
        logger.info("3단계: 임베딩 생성...")
        try:
            embeddings = self.get_embeddings(texts)
        except EmbeddingError as e:
            logger.error(f"임베딩 실패: {e}")
            raise
        
        # 4. 클러스터링
        logger.info("4단계: 클러스터링...")
        try:
            clusters = self.cluster_articles(embeddings, valid_articles, n_clusters)
        except ClusteringError as e:
            logger.error(f"클러스터링 실패: {e}")
            raise
        
        # 5. 요약
        logger.info("5단계: 요약 생성...")
        results = self.summarize_all_clusters(clusters)
        
        logger.info(f"=== 완료: {len(results)}개 그룹 생성 ===")
        
        return results


def print_results(results: List[Dict]) -> None:
    """결과를 보기 좋게 출력"""
    if not results:
        print("\n❌ 결과가 없습니다.")
        return
        
    for result in results:
        print(f"\n{'='*60}")
        print(f"[그룹 {result['cluster_id'] + 1}] - {result['size']}개 기사")
        print(f"{'='*60}")
        print(f"\n📰 대표 기사: {result['representative_title']}")
        if result.get('representative_url'):
            print(f"   🔗 {result['representative_url']}")
        print(f"\n📝 요약:\n{result['summary']}")
        
        if result['related_titles']:
            print(f"\n🔗 관련 기사:")
            for title in result['related_titles']:
                print(f"   - {title}")


if __name__ == "__main__":
    try:
        summarizer = NewsSummarizer()

        keyword = input("검색어를 입력하세요: ").strip()
        if not keyword:
            print("❌ 검색어를 입력해주세요.")
            exit(1)
            
        engine = input("검색엔진 (네이버/다음): ").strip()
        if engine not in ('네이버', '다음'):
            print("❌ '네이버' 또는 '다음'을 입력해주세요.")
            exit(1)
            
        press_choice = None

        print("\n언론사를 선택하세요:")
        print("  0. 전체 (필터 없음)")
        for key, values in PRESS_LIST.items():
            print(f"  {key}. {values[0]}")

        choice = input("\n선택 (번호): ").strip()
        if choice != "0" and choice in PRESS_LIST:
            press_choice = choice
            print(f"✅ {PRESS_LIST[choice][0]} 선택됨")

        results = summarizer.run(keyword, engine, max_articles=20, n_clusters=3, press_choice=press_choice)
        print_results(results)
        
    except ValueError as e:
        print(f"\n❌ 설정 오류: {e}")
    except NewsSearchError as e:
        print(f"\n❌ 검색 오류: {e}")
    except EmbeddingError as e:
        print(f"\n❌ 임베딩 오류: {e}")
    except ClusteringError as e:
        print(f"\n❌ 클러스터링 오류: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")