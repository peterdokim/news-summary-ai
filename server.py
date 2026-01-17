from flask import Flask, request, jsonify
from flask_cors import CORS
from api.news_summarizer import NewsSummarizer
import os
import traceback

app = Flask(__name__)
CORS(app)

# Initialize the news summarizer
summarizer = NewsSummarizer()

@app.route('/api/summarize', methods=['POST'])
def summarize_news():
    """
    API endpoint to summarize news articles

    Request body:
    {
        "keyword": str,
        "max_articles": int (optional, default: 20),
        "n_clusters": int (optional, default: 3)
    }
    """
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

        max_articles = data.get('max_articles', 20)
        n_clusters = data.get('n_clusters', 3)

        # Run the summarizer
        results = summarizer.run(
            keyword=keyword,
            max_articles=max_articles,
            n_clusters=n_clusters
        )

        if not results:
            return jsonify({
                'success': False,
                'error': f"'{keyword}'에 대한 유효한 뉴스 기사가 없습니다."
            }), 404

        return jsonify({
            'success': True,
            'keyword': keyword,
            'results': results,
            'total_clusters': len(results)
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        traceback.print_exc()

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
