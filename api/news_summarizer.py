import os
import requests
import urllib.parse
import numpy as np
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances


os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
load_dotenv()

class NewsSummarizer:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/143.0.0.0 Safari/537.36"
            )
        }

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY가 설정되지 않았습니다.\n"
                "1. .env 파일을 만들고 OPENAI_API_KEY=sk-xxx 형식으로 저장하세요.\n"
                "2. 또는 환경변수로 설정하세요: export OPENAI_API_KEY=sk-xxx"
            )
        
        self.client = OpenAI(api_key=api_key)

    def get_news_url(self, keyword: str, max_articles: int) -> List[str]:
        encoded = urllib.parse.quote(keyword)
        """네이버 뉴스 검색에서 기사 URL 수집"""
        url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={encoded}"

        resp = requests.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        news_urls = []
        
        domains = [
            "news.naver.com",
            "m.entertain.naver.com",
            "m.sports.naver.com"
        ]
        
        # 기사 리스트 요소
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

            if any(domain in href for domain in domains):
                if href not in news_urls:
                    news_urls.append(href)

                if len(news_urls)  >= max_articles:
                    break

        return news_urls

    def extract_news_article(self, url: str) -> Dict[str, str]:
        """BeautifulSoup을 사용하여 기사 텍스트 추출"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 제목 추출
            title_elem = (
                soup.select_one("#title_area") or                      # 일반 뉴스
                soup.select_one('h2.ArticleHead_article_title__qh8GV') # 스포츠/엔터
            )
        
            title = title_elem.get_text(strip=True) if title_elem else None

            # 본문 추출
            article = (
                soup.select_one("#dic_area") or             # 일반 뉴스
                soup.select_one("div._article_content")     # 스포츠/엔터
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
        
        except requests.RequestException as e:
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': f'요청 실패: {str(e)}',
            }
        except Exception as e:
            return {
                'url': url,
                'title': None,
                'text': None,
                'success': False,
                'error': f'파싱 실패: {str(e)}',
            }
        
    def crawl_news(self, keyword: str, max_articles: int = 5) -> List[Dict[str, str]]:
        """
        키워드로 뉴스 검색 → 모든 기사 본문 추출
        
        Args:
            keyword: 검색 키워드
            max_articles: 최대 기사 수
        
        Returns:
            기사 정보 리스트 (제목, 본문, URL 등)
        """
        urls = self.get_news_url(keyword, max_articles)

        articles = []
        for url in urls:
            result = self.extract_news_article(url)
            articles.append(result)

        return articles

    def prepare_articles_for_embedding(self, articles: List[Dict]) -> tuple[List[Dict], List[str]]:
        """
        크롤링 결과에서 성공한 기사만 추출하고 임베딩용 텍스트 준비

        Args:
            articles: 크롤링 결과 (기사 정보 리스트)

        Returns:
            (valid_articles, texts_for_embedding)
            - valid_articles: 성공한 기사 리스트
            - texts_for_embedding: 임베딩할 텍스트 리스트
        """
        valid_articles = []
        texts_for_embedding = []

        for article in articles:
            if not article['success']:
                continue
            if not article.get('text'):
                continue

            valid_articles.append(article)

            title = article.get('title') or ''
            text = article.get('text') or ''

            combined = f"[제목] {title}\n\n[본문] {text[:1500]}"
            texts_for_embedding.append(combined)
        
        return valid_articles, texts_for_embedding
        
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        기사 텍스트 리스트를 벡터로 변환

        Args:
            texts: 변환할 텍스트 리스트

        Returns:
            numpy 배열 (texts 개수 x 1536 차원)
        """
        if not self.client:
            raise ValueError("OpenAI 클라이언트가 초기화되지 않았습니다.")

        texts = [t if t else " " for t in texts]

        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        embeddings = [item.embedding for item in response.data]
        
        return np.array(embeddings)
    
    def cluster_articles(
        self, embeddings: np.ndarray, articles: List[Dict],
        n_clusters: int = 3) -> List[Dict]:
        """
        임베딩 벡터를 기반으로 기사들을 클러스터링

        Args:
            embeddings: 임베딩 벡터 배열 (기사 수 x 1536)
            articles: 기사 정보 리스트
            n_clusters: 클러스터 개수

        Returns:
            클러스터별 기사 정보 리스트
            [
                {
                    'cluster_id': 0,
                    'articles' : [기사1, 기사2, ...],
                    'representative': 대표 기사,
                },
                ...
            ]
        """
        n_clusters = min(n_clusters, len(articles))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        clusters = []
        for cluster_id in range(n_clusters):
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
            
        return clusters
    
    def summarize_cluster(self, cluster: Dict) -> Dict:
        """
        클러스터의 대표 기사 요약 + 관련 기사 제목 리스트
        
        Returns:
            {
                'cluster_id': 클러스터 ID,
                'size': 기사 개수,
                'summary': 대표 기사 요약,
                'representative_title': 대표 기사 제목,
                'related_titles': 관련 기사 제목 리스트
            }
        """
        representative = cluster['representative']
        text = representative.get('text', '')
        
        # 대표 기사 요약
        if text:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 변경
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
                        "content": text
                    }
                ],
                max_tokens=300,      # 원래대로
                temperature=0.3      # 원래대로
            )
            summary = response.choices[0].message.content
        else:
            summary = "요약할 내용이 없습니다."
        
        # 관련 기사 제목 리스트 (대표 기사 제외)
        related_titles = [
            article['title'] 
            for article in cluster['articles'] 
            if article['title'] != representative['title']
        ]
        
        return {
            'cluster_id': cluster['cluster_id'],
            'size': cluster['size'],
            'summary': summary,
            'representative_title': representative['title'],
            'related_titles': related_titles
        }


    def summarize_all_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """모든 클러스터 요약"""
        results = []
        for cluster in clusters:
            result = self.summarize_cluster(cluster)
            results.append(result)
        return results
    
    def run(self, keyword: str, max_articles: int = 20, n_clusters: int =3) -> List[Dict]:
        """
        전체 파이프라인 실행: 크롤링 -> 임베딩 -> 클러스터링 -> 요약

        Args:
            keyword: 검색 키워드
            max_articles: 최대 크롤링 기사 수
            n_clusters: 클러스터 개수

        Returns:
            클러스터별 요약 결과 리스트
        """
        
        articles = self.crawl_news(keyword, max_articles)
        valid_articles, texts = self.prepare_articles_for_embedding(articles)
        
        if len(valid_articles) == 0:
            print(f"❌ '{keyword}'에 대한 유효한 뉴스 기사가 없습니다.")
            return [] 
        
        embeddings = self.get_embeddings(texts)
        clusters = self.cluster_articles(embeddings, valid_articles, n_clusters)
        results = self.summarize_all_clusters(clusters)
        
        return results

if __name__ == "__main__": 
    summarizer = NewsSummarizer()

    keyword = input("검색어를 입력하세요: ")
    results = summarizer.run(keyword, max_articles=20, n_clusters=3)
    
    for result in results:
        print(f"\n{'='*60}")
        print(f"[그룹 {result['cluster_id'] + 1}] - {result['size']}개 기사")
        print(f"{'='*60}")
        print(f"\n📰 대표 기사: {result['representative_title']}")
        print(f"\n📝 요약:\n{result['summary']}")
        
        if result['related_titles']:
            print(f"\n🔗 관련 기사:")
            for title in result['related_titles']:
                print(f"   - {title}")
    
    
   
    