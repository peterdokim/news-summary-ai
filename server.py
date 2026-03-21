from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional 
from api.news_summarizer import NewsSummarizer, NewsSearchError, EmbeddingError, ClusteringError
import os
import traceback
import threading
import uuid
import time
import logging
from fastapi.responses import JSONResponse
import uvicorn


class SummarizeRequest(BaseModel):
    keyword: str
    search_engine: Optional[str] = '네이버'
    max_articles: Optional[int] = 20
    n_clusters: Optional[int] = 3
    press_choice: Optional[str] = None
# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize the news summarizer
try:
    summarizer = NewsSummarizer()
    logger.info("✅ NewsSummarizer initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize NewsSummarizer: {e}")
    summarizer = None

# Background job store
jobs = {}
jobs_lock = threading.Lock()


def cleanup_old_jobs():
    """Remove jobs older than 30 minutes."""
    cutoff = time.time() - 1800
    with jobs_lock:
        expired = [jid for jid, j in jobs.items() if j['created_at'] < cutoff]
        for jid in expired:
            del jobs[jid]
            
@app.get('/')
@app.get('/api/health')
@app.head('/')
@app.head('/api/health')
def health():
    return {'status': 'ok'}


@app.post('/api/summarize')
def summarize_news(body: SummarizeRequest):
    
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
        return {
            'success': False,
            'error': 'Server not properly initialized. Please check your OpenAI API key.'
        }

    try:
        keyword = body.keyword
        search_engine = body.search_engine
        max_articles = body.max_articles
        n_clusters = body.n_clusters
        

        logger.info(f"🔍 Request received: keyword='{keyword}', search_engine='{search_engine}', max_articles={max_articles}")

        # Run the summarizer
        results = summarizer.run(
            keyword=keyword,
            search_engine=search_engine,
            max_articles=max_articles,
            n_clusters=n_clusters
        )

        if not results:
            return {
                'success': False,
                'error': f"'{keyword}'에 대한 유효한 뉴스 기사가 없습니다."
            }

        logger.info(f"완료: {len(results)}개 클러스터 생성")

        return {
            'success': True,
            'keyword': keyword,
            'search_engine': search_engine,
            'results': results,
            'total_clusters': len(results)
        }

    except ValueError as e:
        logger.warning(f"입력값 오류: {e}")
        return JSONResponse({
            'success': False,
            'error': str(e)
        },status_code=400)
    except NewsSearchError as e:
        logger.error(f"뉴스 검색 오류: {e}")
        return JSONResponse({
            'success': False,
            'error': f"뉴스 검색 실패: {str(e)}"
        },status_code=400)
    except EmbeddingError as e:
        logger.error(f"임베딩 생성 오류: {e}")
        return JSONResponse({
            'success': False,
            'error': f"임베딩 생성 실패: {str(e)}"
        },status_code=500)
    except ClusteringError as e:
        logger.error(f"클러스터링 오류: {e}")
        return JSONResponse({
            'success': False,
            'error': f"클러스터링 실패: {str(e)}"
        },status_code=500)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"서버 오류: {error_msg}\n{traceback.format_exc()}")

        # Check for OpenAI quota error
        if 'quota' in error_msg.lower() or '429' in error_msg:
            return JSONResponse({
                'success': False,
                'error': 'OpenAI API 할당량이 초과되었습니다. 계정 결제 정보를 확인하세요.',
                'details': error_msg
            },status_code=429)

        return JSONResponse({
            'success': False,
            'error': '서버 오류가 발생했습니다.',
            'details': error_msg
        },status_code=500)

@app.post('/api/summarize-start')
def summarize_start(body: SummarizeRequest):
    
    """Start a background summarization job and return a job_id immediately."""

    if not summarizer:
        logger.error("NewsSummarizer not initialized for background job")
        return JSONResponse({
            'success': False,
            'error': 'Server not properly initialized. Please check your OpenAI API key.'
        }, status_code=500)

    keyword = body.keyword
    if not keyword:
        return JSONResponse({'success': False, 'error': '검색어를 입력해주세요'},status_code=400)

    max_articles = body.max_articles
    n_clusters = body.n_clusters
    search_engine = body.search_engine

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {
            'progress': 0,
            'message': '시작 중...',
            'result': None,
            'error': None,
            'done': False,
            'keyword': keyword,
            'search_engine': search_engine,
            'created_at': time.time(),
        }

    def run_job():
        def progress_callback(percent, message):
            with jobs_lock:
                if job_id in jobs:
                    jobs[job_id]['progress'] = percent
                    jobs[job_id]['message'] = message

        try:
            results = summarizer.run(
                keyword=keyword,
                search_engine=search_engine,
                max_articles=max_articles,
                n_clusters=n_clusters,
                progress_callback=progress_callback,
            )
            with jobs_lock:
                jobs[job_id]['result'] = results
                jobs[job_id]['done'] = True
        except Exception as e:
            error_msg = str(e)
            print(f"Job {job_id} error: {error_msg}")
            traceback.print_exc()
            with jobs_lock:
                jobs[job_id]['error'] = error_msg
                jobs[job_id]['done'] = True
        finally:
            cleanup_old_jobs()

    thread = threading.Thread(target=run_job, daemon=True)
    thread.start()

    return JSONResponse({'success': True, 'job_id': job_id},status_code=202)


@app.get('/api/progress/{job_id}')
def get_progress(job_id:str):
    """Return current progress of a background summarization job."""
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return JSONResponse({'error': 'Job not found'},status_code=404)
    return JSONResponse({
        'progress': job['progress'],
        'message': job['message'],
        'done': job['done'],
        'error': job['error'],
        'result': job['result'] if job['done'] and not job['error'] else None,
        'keyword': job['keyword'],
        'search_engine': job['search_engine'],
    })


# @app.get('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return JSONResponse({
#         'status': 'healthy',
#         'service': 'ANS News Summarizer API'
#     },status_code=200)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    

    print(f"Starting Flask server on port {port}...")
    print(f"API endpoint: http://localhost:{port}/api/summarize")

    uvicorn.run(app,host='0.0.0.0', port=port)
