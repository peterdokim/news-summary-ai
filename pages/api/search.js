export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { keyword, source, limit } = req.body;

  if (!keyword || !keyword.trim()) {
    return res.status(400).json({
      success: false,
      error: '검색어를 입력해주세요'
    });
  }

  try {
    const pythonApiUrl = process.env.PYTHON_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000');
    const response = await fetch(`${pythonApiUrl}/api/summarize-start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keyword: keyword.trim(),
        max_articles: limit || 5,
        n_clusters: 3,
        search_engine: source === 'naver' ? '네이버' : '다음',
      }),
    });

    if (!response.ok) {
      throw new Error('Python backend returned an error');
    }

    const data = await response.json();

    return res.status(202).json({
      success: true,
      job_id: data.job_id,
      keyword,
      source,
      limit,
    });

  } catch (error) {
    console.error('API Error:', error);
    return res.status(500).json({
      success: false,
      error: 'Flask 서버에 연결할 수 없습니다. Python 백엔드가 실행 중인지 확인하세요.',
      details: error.message
    });
  }
}
