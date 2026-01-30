export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { keyword, source, limit } = req.body;

  console.log('📍 search.js received:', { keyword, source, limit });

  if (!keyword || !keyword.trim()) {
    return res.status(400).json({
      success: false,
      error: '검색어를 입력해주세요'
    });
  }

  try {
    // Call Python backend API
    // In production (Vercel), use relative URL; in development, use localhost
    const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
    const searchEngine = source === 'daum' ? '다음' : '네이버';
    
    console.log('🔄 Sending to backend:', { searchEngine, keyword, limit });
    
    const response = await fetch(`${pythonApiUrl}/api/summarize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        keyword: keyword.trim(),
        search_engine: searchEngine,
        max_articles: limit || 20,
        n_clusters: 3
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('유효한 뉴스 기사가 없습니다', response.status, errorData);
      throw new Error(errorData.error || `Python backend returned status ${response.status}`);
    }

    const data = await response.json();

    return res.status(200).json({
      success: true,
      keyword,
      source,
      limit,
      results: data.results || data,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('API Error:', error);
    const errorMessage = error.message || 'Unknown error';
    const isConnectionError = errorMessage.includes('fetch') || errorMessage.includes('ECONNREFUSED');
    
    return res.status(500).json({
      success: false,
      error: isConnectionError 
        ? 'Flask 서버에 연결할 수 없습니다. "python server.py"를 실행 중인지 확인하세요. (포트 5000)' 
        : `${errorMessage}`,
      details: errorMessage
    });
  }
}
