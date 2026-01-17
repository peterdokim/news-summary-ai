from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/python/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ANS News Summarizer API'
    }), 200

# For Vercel serverless
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
