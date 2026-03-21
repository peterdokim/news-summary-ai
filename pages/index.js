import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [source, setSource] = useState('naver');
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const history = JSON.parse(localStorage.getItem('ansSearchHistory') || '[]');
    setSearchHistory(history);
  }, []);

  const addToHistory = (kw, src, lim) => {
    const newEntry = {
      id: Date.now(),
      keyword: kw,
      source: src,
      limit: lim,
      timestamp: new Date().toLocaleString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }),
    };
    const updated = [newEntry, ...searchHistory].slice(0, 30);
    setSearchHistory(updated);
    localStorage.setItem('ansSearchHistory', JSON.stringify(updated));
    return newEntry.id;
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) {
      setError('검색어를 입력해주세요');
      return;
    }
    setLoading(true);
    setProgress(0);
    setProgressMessage('시작 중...');
    setError('');

    try {
      // 1. Start the background job
      const startRes = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword, source, limit }),
      });
      const startData = await startRes.json();
      if (!startData.success) {
        setError(startData.error || '검색을 시작할 수 없습니다');
        setLoading(false);
        return;
      }

      const { job_id } = startData;

      // 2. Poll progress until done
      const poll = async () => {
        try {
          const progressRes = await fetch(`/api/progress?jobId=${job_id}`);
          const progressData = await progressRes.json();

          setProgress(progressData.progress || 0);
          setProgressMessage(progressData.message || '');

          if (!progressData.done) {
            setTimeout(poll, 600);
            return;
          }

          // Job finished
          if (progressData.error) {
            setError(progressData.error);
            setLoading(false);
            return;
          }

          if (!progressData.result || progressData.result.length === 0) {
            setError(`'${keyword}'에 대한 유효한 뉴스 기사가 없습니다.`);
            setLoading(false);
            return;
          }

          // Build the result object matching the shape news.js expects
          const data = {
            success: true,
            keyword: startData.keyword,
            source: startData.source,
            limit: startData.limit,
            results: progressData.result,
          };

          const entryId = addToHistory(keyword, source, limit);
          try {
            localStorage.setItem(`ansResult_${entryId}`, JSON.stringify(data));
          } catch {
            // localStorage full, skip caching
          }
          sessionStorage.setItem('newsResults', JSON.stringify(data));
          router.push('/news');
        } catch {
          setError('진행 상황을 가져오는 중 오류가 발생했습니다.');
          setLoading(false);
        }
      };

      setTimeout(poll, 600);
    } catch {
      setError('서버 연결에 실패했습니다. Flask 서버가 실행 중인지 확인하세요.');
      setLoading(false);
    }
  };

  const handleHistoryClick = (entry) => {
    const stored = localStorage.getItem(`ansResult_${entry.id}`);
    if (stored) {
      sessionStorage.setItem('newsResults', stored);
      router.push('/news');
    } else {
      setKeyword(entry.keyword);
      setSource(entry.source);
      setLimit(entry.limit);
      setError('');
    }
  };

  const removeHistoryEntry = (id, e) => {
    e.stopPropagation();
    const updated = searchHistory.filter((h) => h.id !== id);
    setSearchHistory(updated);
    localStorage.setItem('ansSearchHistory', JSON.stringify(updated));
  };

  const handleHistoryKeyDown = (event, entry) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleHistoryClick(entry);
    }
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('ansSearchHistory');
  };

  return (
    <>
      <Head>
        <title>ANS - AI News Summarizer</title>
        <meta name="description" content="AI-powered news summarization tool" />
        <link
          rel="icon"
          href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>"
        />
      </Head>

      <div className="flex min-h-screen bg-gray-50">

        {/* ── Sidebar ── */}
        <aside className={`${sidebarOpen ? 'w-60' : 'w-12'} bg-gray-900 text-white hidden md:flex flex-col fixed inset-y-0 left-0 z-20 overflow-hidden transition-all duration-300`}>

          {/* Toggle button */}
          <div className={`flex ${sidebarOpen ? 'justify-end px-2' : 'justify-center'} pt-3 pb-1`}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sidebarOpen ? "M15 19l-7-7 7-7" : "M9 5l7 7-7 7"} />
              </svg>
            </button>
          </div>

          {sidebarOpen && (
            <>
              {/* Logo */}
              <Link href="/">
                <div className="flex items-center gap-3 px-4 py-3 hover:bg-gray-800 transition-colors cursor-pointer">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center font-black text-sm select-none">
                    A
                  </div>
                  <div>
                    <div className="font-black tracking-widest text-base leading-tight">A N S</div>
                    <div className="text-xs text-gray-400 leading-tight">AI News Summarizer</div>
                  </div>
                </div>
              </Link>

              {/* Nav */}
              <nav className="px-2 pb-3 border-b border-gray-800">
                <Link href="/">
                  <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gray-800 text-white cursor-pointer">
                    <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span className="text-sm font-medium">뉴스 검색</span>
                  </div>
                </Link>
              </nav>

              {/* Search History */}
              <div className="flex-1 overflow-y-auto px-2 pt-3 pb-4">
                <div className="flex items-center justify-between px-3 mb-2">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">최근 검색</span>
                  {searchHistory.length > 0 && (
                    <button onClick={clearHistory} className="text-xs text-gray-600 hover:text-gray-300 transition-colors">
                      전체 삭제
                    </button>
                  )}
                </div>

                {searchHistory.length === 0 ? (
                  <div className="px-3 py-6 text-center text-gray-600 text-xs leading-relaxed">
                    검색 기록이 없습니다
                  </div>
                ) : (
                  <div className="space-y-0.5">
                    {searchHistory.map((entry) => (
                      <div
                        key={entry.id}
                        onClick={() => handleHistoryClick(entry)}
                        onKeyDown={(e) => handleHistoryKeyDown(e, entry)}
                        role="button"
                        tabIndex={0}
                        className="w-full text-left flex items-start gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors group"
                      >
                        <svg className="w-3.5 h-3.5 text-gray-600 mt-0.5 flex-shrink-0 group-hover:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="min-w-0 flex-1">
                          <div className="text-sm text-gray-300 truncate group-hover:text-white font-medium">
                            {entry.keyword}
                          </div>
                          <div className="text-xs text-gray-600 mt-0.5">
                            {entry.source === 'naver' ? 'Naver' : 'Daum'} · {entry.limit}개 · {entry.timestamp}
                          </div>
                        </div>
                        <button onClick={(e) => removeHistoryEntry(entry.id, e)} className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-gray-300 transition-all flex-shrink-0 p-0.5">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom footer */}
              <div className="px-4 py-3 border-t border-gray-800">
                <p className="text-xs text-gray-600">Powered by OpenAI</p>
              </div>
            </>
          )}
        </aside>

        {/* ── Main Content ── */}
        <main className={`${sidebarOpen ? 'md:ml-60' : 'md:ml-12'} flex-1 flex items-center justify-center min-h-screen p-8 transition-all duration-300`}>
          <div className="w-full max-w-lg">

            {/* Heading */}
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">무엇을 찾고 싶으신가요?</h1>
              <p className="text-gray-500 text-sm">키워드를 입력하면 AI가 뉴스를 요약해 드립니다</p>
            </div>

            {/* Search Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-7">
              <form onSubmit={handleSearch} className="space-y-4">

                {/* Keyword Input */}
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="검색할 키워드를 입력하세요..."
                    className="w-full pl-11 pr-4 py-3.5 text-gray-900 border border-gray-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-100 outline-none transition-all placeholder-gray-400"
                  />
                </div>

                {/* Options */}
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1.5 text-center">
                      뉴스 소스
                    </label>
                    <select
                      value={source}
                      onChange={(e) => setSource(e.target.value)}
                      className="w-full px-3 py-2.5 border border-gray-500 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-100 outline-none bg-white text-gray-700 text-center"
                    >
                      <option value="naver">Naver</option>
                      <option value="daum">Daum</option>
                    </select>
                  </div>
                  
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3.5 rounded-xl font-semibold hover:shadow-lg hover:shadow-purple-200 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  검색하기
                </button>

                {/* Progress bar */}
                {loading && (
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="truncate pr-2">{progressMessage}</span>
                      <span className="flex-shrink-0 font-medium text-purple-600">{progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Error */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-2 text-sm text-red-700">
                    <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                  </div>
                )}
              </form>
            </div>

            <p className="text-center text-xs text-gray-400 mt-5">
              예시: &quot;AI&quot;, &quot;경제&quot;, &quot;주식&quot;, &quot;기술&quot;, &quot;스포츠&quot;
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
