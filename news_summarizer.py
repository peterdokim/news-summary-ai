import os
import requests
import urllib.parse
import numpy as np
from bs4 import BeautifulSoup
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

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

            if href and "news.naver.com" in href:
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
            title_html = soup.select_one("#title_area")
            title = title_html.get_text(strip=True) if title_html else None

            # 본문 추출
            article = soup.select_one("#dic_area")
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
            texts: 

        Returns:
            np.ndarray: _description_
        """
        return 

if __name__ == "__main__": 
    summarizer = NewsSummarizer()
    keyword = input("검색어를 입력하세요: ")
    articles = summarizer.crawl_news(keyword)
    valid_articles, texts = summarizer.prepare_articles_for_embedding(articles)
    print(texts)
