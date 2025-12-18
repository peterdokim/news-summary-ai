import requests
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict

class NewsSummarizer:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/143.0.0.0 Safari/537.36"
            )
        }

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
            
            news_url = None

            if href and "news.naver.com" in href:
                news_url = href
            
            if not news_url:
                continue

            if news_url in news_urls:
                continue

            news_urls.append(news_url)

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
        
if __name__ == "__main__": 
    crawler = NewsSummarizer()
    keyword = input("검색어를 입력하세요: ")
    print(crawler.crawl_news(keyword))
    
    