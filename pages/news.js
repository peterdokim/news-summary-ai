import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';

export default function News() {
  const router = useRouter();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    const storedResults = sessionStorage.getItem('newsResults');
    if (storedResults) {
      const data = JSON.parse(storedResults);
      setResults(data);
      setLoading(false);
    } else {
      router.push('/');
    }
    const History = JSON.parse(localStorage.getItem('ansSearchHistory') || '[]');
    setSearchHistory(History);
  }, [router]);

  const handleHistoryClick = (entry) => {
    const stored = localStorage.getItem(`ansResult_${entry.id}`);
    if (stored) {
      const data = JSON.parse(stored);
      sessionStorage.setItem('newsResults', stored);
      setResults(data);
      setSelectedIndex(0);
    }
  };


  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('ansSearchHistory');
  };

  const removeHistoryEntry = (id,e) => {
    e.stopPropagation();
    const updated = searchHistory.filter((h) => h.id !== id);
    setSearchHistory(updated);
    localStorage.setItem('ansSearchHistory', JSON.stringify(updated));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className= "text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-500 text-sm">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!results || !results.success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-3xl p-8 max-w-md text-center shadow-xl">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">오류 발생</h2>
          <p className="text-gray-600 mb-6">{results?.error || '결과를 불러올 수 없습니다.'}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
          >
            홈으로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  const clusters = results.results || [];
  const selected = clusters[selectedIndex];

  return (
    <>
      <Head>
        <title>{results.keyword} - ANS</title>
        <meta name="description" content="AI News Summary Results" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>" />
      </Head>

      <div className="flex h-screen bg-gray-50 overflow-hidden">

          {/* ── Sidebar ── */}
        <aside className="w-60 flex-shrink-0 bg-gray-900 text-white flex flex-col overflow-y-auto">

          {/* Logo */}
          <Link href="/">
            <div className="flex items-center gap-3 px-4 py-5 hover:bg-gray-800 transition-colors cursor-pointer">
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
              <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white cursor-pointer transition-colors">
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
              <div className="px-3 py-6 text-center text-gray-600 text-xs">검색 기록이 없습니다</div>
            ) : (
              <div className="space-y-0.5">
                {searchHistory.map((entry) => (
                  <button
                    key={entry.id}
                    onClick={() => handleHistoryClick(entry)}
                    className="w-full text-left flex items-start gap-2 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors group"
                  >
                    <svg className="w-3.5 h-3.5 text-gray-600 mt-0.5 flex-shrink-0 group-hover:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm text-gray-300 truncate group-hover:text-white font-medium">{entry.keyword}</div>
                      <div className="text-xs text-gray-600 mt-0.5">{entry.source === 'naver' ? 'Naver' : 'Daum'} · {entry.limit}개 · {entry.timestamp}</div>
                    </div>
                    <button onClick={(e) => removeHistoryEntry(entry.id, e)} className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-gray-300 transition-all flex-shrink-0 p-0.5">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="px-4 py-3 border-t border-gray-800">
            <p className="text-xs text-gray-600">Powered by OpenAI</p>
          </div>
        </aside>

        {/* ── Article List Panel ── */}
        <div className="w-80 flex-shrink-0 bg-white border-r border-gray-200 flex flex-col overflow-hidden">

          {/* Panel Header */}
          <div className="px-4 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2 mb-1">
              <button
                onClick={() => router.push('/')}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h2 className="font-bold text-gray-800 truncate text-sm">
                &quot;{results.keyword}&quot; 검색 결과
              </h2>
            </div>
            <p className="text-xs text-gray-400 pl-6">뉴스 그룹 {clusters.length}개</p>
          </div>

          {/* Cluster List */}
          <div className="flex-1 overflow-y-auto p-2">
            {clusters.map((cluster, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedIndex(idx)}
                className={`w-full text-left p-3 rounded-xl mb-1.5 transition-all border ${
                  selectedIndex === idx
                    ? 'bg-purple-50 border-purple-200 border-l-4 border-l-purple-500'
                    : 'border-transparent hover:bg-gray-50 hover:border-gray-100'
                }`}
              >
                <div className="flex gap-2.5">
                  {cluster.representative_image && (
                    <img
                      src={cluster.representative_image}
                      alt=""
                      className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-bold ${selectedIndex === idx ? 'text-purple-600' : 'text-gray-400'}`}>
                        그룹 {idx + 1}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full">
                        {cluster.size}개
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 font-medium line-clamp-2 leading-snug">
                      {cluster.representative_title}
                    </p>
                    {cluster.related_titles?.length > 0 && (
                      <p className="text-xs text-gray-400 mt-1">
                        관련 기사 {cluster.related_titles.length}개
                      </p>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Summary Panel ── */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          {!selected ? (
            <div className="flex items-center justify-center h-full text-gray-400 text-sm">
              기사를 선택하세요
            </div>
          ) : (
            <div className="max-w-2xl mx-auto px-8 py-10">

              {/* Group label */}
              <p className="text-xs font-bold text-purple-600 uppercase tracking-wider mb-2">
                그룹 {selected.cluster_id + 1}
              </p>

              {/* Representative article title */}
              <h1 className="text-2xl font-bold text-gray-900 mb-3 leading-snug">
                <a
                  href={selected.representative_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-purple-600 transition-colors"
                >
                  {selected.representative_title}
                </a>
              </h1>
              <a
                href={selected.representative_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-500 hover:underline mb-6"
              >
                원문 보기
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>

              {/* Hero Image */}
              {selected.representative_image && (
                <img
                  src={selected.representative_image}
                  alt={selected.representative_title}
                  className="w-full rounded-2xl object-cover max-h-72 mb-6"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              )}

              {/* AI Summary Card */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                  <h3 className="font-semibold text-gray-700">AI 요약</h3>
                </div>
                <p className="text-gray-700 leading-relaxed text-sm">{selected.summary}</p>
              </div>

              {/* Related Articles */}
              {selected.related_titles?.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                    관련 기사 {selected.related_titles.length}개
                  </h3>
                  <div className="space-y-2">
                    {selected.related_titles.map((title, idx) => (
                      <div
                        key={idx}
                        className="flex items-center gap-3 p-3.5 bg-white rounded-xl border border-gray-100"
                      >
                        <span className="text-xs font-bold text-purple-400 w-5 flex-shrink-0">{idx + 1}</span>
                        <span className="text-sm text-gray-700 flex-1 leading-snug">{title}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>

      </div>
    </>
  );
}