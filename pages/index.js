import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Header from '@/components/Header';

export default function Home() {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');
  const [source, setSource] = useState('naver');
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!keyword.trim()) {
      setError('검색어를 입력해주세요');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword, source, limit })
      });

      const data = await response.json();

      if (data.success) {
        sessionStorage.setItem('newsResults', JSON.stringify(data));
        router.push('/news');
      } else {
        setError(data.error || '검색 중 오류가 발생했습니다');
      }
    } catch (err) {
      setError('서버 연결에 실패했습니다. Flask 서버가 실행 중인지 확인하세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>ANS - AI News Summarizer</title>
        <meta name="description" content="AI-powered news summarization tool" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">

        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
        </div>

        {/* Main Content */}
        <div className="relative flex items-center justify-center min-h-screen p-6">
          <div className="max-w-2xl w-full">
            
            {/* Logo & Title Section */}
            <Header />

            {/* Search Card */}
            <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-10 border border-white/20 transform hover:shadow-purple-500/20 transition-all duration-300">
              <form onSubmit={handleSearch} className="space-y-6">
                
                {/* Keyword Input */}
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl blur opacity-0 group-hover:opacity-30 transition-opacity"></div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                      <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <input
                      type="text"
                      value={keyword}
                      onChange={(e) => setKeyword(e.target.value)}
                      placeholder="검색할 키워드를 입력하세요..."
                      className="w-full pl-14 pr-6 py-5 text-lg text-gray-900 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 outline-none transition-all placeholder-gray-400"
                    />
                  </div>
                </div>

                {/* Options Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="relative">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      뉴스 소스
                    </label>
                    <select
                      value={source}
                      onChange={(e) => setSource(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 outline-none cursor-pointer transition-all bg-black hover:border-purple-300"
                    >
                      <option value="naver">🔍 Naver</option>
                      <option value="google">🌐 Google</option>
                    </select>
                  </div>

                  <div className="relative">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      기사 개수
                    </label>
                    <select
                      value={limit}
                      onChange={(e) => setLimit(Number(e.target.value))}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 outline-none cursor-pointer transition-all bg-black hover:border-purple-300"
                    >
                      <option value={5}>5개 기사</option>
                      <option value={10}>10개 기사</option>
                      <option value={20}>20개 기사</option>
                    </select>
                  </div>
                </div>

                {/* Search Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="group relative w-full bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 text-white py-5 rounded-xl font-bold text-lg overflow-hidden transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/50 hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-400 via-blue-400 to-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="relative flex items-center justify-center gap-3">
                    {loading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span>뉴스를 검색하는 중...</span>
                      </>
                    ) : (
                      <>
                        <svg className="h-6 w-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <span>검색하기</span>
                      </>
                    )}
                  </div>
                </button>

                {/* Error Message */}
                {error && (
                  <div className="animate-shake bg-red-50 border-2 border-red-200 rounded-xl p-4 flex items-start gap-3">
                    <svg className="h-6 w-6 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="flex-1">
                      <p className="font-semibold text-red-800">오류 발생</p>
                      <p className="text-red-600 text-sm mt-1">{error}</p>
                    </div>
                  </div>
                )}
              </form>

             {/*  {/* Info Cards 
              <div className="mt-8 grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-100">
                  <div className="text-3xl mb-2">🤖</div>
                  <p className="text-xs font-semibold text-gray-700">AI 요약</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                  <div className="text-3xl mb-2">⚡</div>
                  <p className="text-xs font-semibold text-gray-700">실시간</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                  <div className="text-3xl mb-2">📊</div>
                  <p className="text-xs font-semibold text-gray-700">분석</p>
                </div>
              </div> */} 

              {/* Tips */}
              <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">💡</div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-blue-900 mb-1">검색 팁</p>
                    <ul className="text-xs text-blue-700 space-y-1">
                      <li>• 구체적인 키워드를 입력하면 더 정확한 결과를 얻을 수 있어요</li>
                      <li>• 예시: "AI", "경제", "주식", "기술", "스포츠" 등</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="text-center mt-10 space-y-3">
              <div className="flex items-center justify-center gap-2 text-gray-600 text-sm">
                <span>Built with</span>
                <span className="text-red-500 animate-pulse">♥</span>
                <span>by ANS Team</span>
              </div>
              <div className="flex items-center justify-center gap-4 text-gray-500 text-xs">
                <span>Next.js</span>
                <span>•</span>
                <span>OpenAI</span>
                <span>•</span>
                <span>Flask</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(-20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        .animate-fade-in {
          animation: fade-in 1s ease-out;
        }
        
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </>
  );
}