from flask import Flask, request, jsonify
from flask_cors import CORS
from api.news_summarizer import NewsSummarizer, NewsSearchError, EmbeddingError, ClusteringError
import os
import traceback
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the news summarizer
try:
    summarizer = NewsSummarizer()
    logger.info("✅ NewsSummarizer initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize NewsSummarizer: {e}")
    summarizer = None

@app.route('/api/summarize', methods=['POST'])
def summarize_news():
    """
    API endpoint to summarize news articles

    Request body:
    {
        "keyword": str (required),
        "search_engine": str (optional, default: "네이버", choices: "네이버" or "다음"),
        "max_articles": int (optional, default: 20),
        "n_clusters": int (optional, default: 3)
    }
    """
    if not summarizer:
        logger.error("❌ NewsSummarizer not initialized")
        return jsonify({
            'success': False,
            'error': 'Server not properly initialized. Please check your OpenAI API key.'
        }), 500
    
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        keyword = data.get('keyword')
        if not keyword:
            return jsonify({
                'success': False,
                'error': '검색어를 입력해주세요'
            }), 400

        search_engine = data.get('search_engine', '네이버')
        max_articles = data.get('max_articles', 20)
        n_clusters = data.get('n_clusters', 3)

        logger.info(f"🔍 Request received: keyword='{keyword}', search_engine='{search_engine}', max_articles={max_articles}")

        # Run the summarizer
        results = summarizer.run(
            keyword=keyword,
            search_engine=search_engine,
            max_articles=max_articles,
            n_clusters=n_clusters
        )

        if not results:
            return jsonify({
                'success': False,
                'error': f"'{keyword}'에 대한 유효한 뉴스 기사가 없습니다."
            }), 404

        logger.info(f"완료: {len(results)}개 클러스터 생성")

        return jsonify({
            'success': True,
            'keyword': keyword,
            'search_engine': search_engine,
            'results': results,
            'total_clusters': len(results)
        }), 200

    except ValueError as e:
        logger.warning(f"입력값 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except NewsSearchError as e:
        logger.error(f"뉴스 검색 오류: {e}")
        return jsonify({
            'success': False,
            'error': f"뉴스 검색 실패: {str(e)}"
        }), 400
    except EmbeddingError as e:
        logger.error(f"임베딩 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': f"임베딩 생성 실패: {str(e)}"
        }), 500
    except ClusteringError as e:
        logger.error(f"클러스터링 오류: {e}")
        return jsonify({
            'success': False,
            'error': f"클러스터링 실패: {str(e)}"
        }), 500
    except Exception as e:
        error_msg = str(e)
        logger.error(f"서버 오류: {error_msg}\n{traceback.format_exc()}")

        # Check for OpenAI quota error
        if 'quota' in error_msg.lower() or '429' in error_msg:
            return jsonify({
                'success': False,
                'error': 'OpenAI API 할당량이 초과되었습니다. 계정 결제 정보를 확인하세요.',
                'details': error_msg
            }), 429

        return jsonify({
            'success': False,
            'error': '서버 오류가 발생했습니다.',
            'details': error_msg
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ANS News Summarizer API'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    print(f"Starting Flask server on port {port}...")
    print(f"API endpoint: http://localhost:{port}/api/summarize")

    app.run(host='0.0.0.0', port=port, debug=debug)
