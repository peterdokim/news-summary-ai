from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the api directory to path
sys.path.insert(0, os.path.dirname(__file__))

from news_summarizer import NewsSummarizer

# Global instance for warm starts
_summarizer = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        _summarizer = NewsSummarizer()
    return _summarizer

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}

            # Validate input
            keyword = data.get('keyword')
            if not keyword:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '검색어를 입력해주세요'
                }).encode())
                return

            max_articles = data.get('max_articles', 20)
            n_clusters = data.get('n_clusters', 3)

            # Run summarizer
            summarizer = get_summarizer()
            results = summarizer.run(
                keyword=keyword,
                search_engine=search_engine,
                max_articles=max_articles,
                n_clusters=n_clusters
            )

            if not results:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': f"'{keyword}'에 대한 유효한 뉴스 기사가 없습니다."
                }).encode())
                return

            # Success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'keyword': keyword,
                'results': results,
                'total_clusters': len(results)
            }).encode())

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")

            # Check for quota error
            status_code = 500
            if 'quota' in error_msg.lower() or '429' in error_msg:
                status_code = 429
                error_response = {
                    'success': False,
                    'error': 'OpenAI API 할당량이 초과되었습니다.',
                    'details': error_msg
                }
            else:
                error_response = {
                    'success': False,
                    'error': '서버 오류가 발생했습니다.',
                    'details': error_msg
                }

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
