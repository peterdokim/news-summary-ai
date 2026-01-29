import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Header from '@/components/Header';

export default function News() {
  const router = useRouter();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedResults = sessionStorage.getItem('newsResults');
    if (storedResults) {
      const data = JSON.parse(storedResults);
      setResults(data);
      setLoading(false);
    } else {
      router.push('/');
    }
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-gray-800 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-xl">로딩 중...</p>
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

  return (
    <>
      <Head>
        <title>검색 결과 - ANS</title>
        <meta name="description" content="AI News Summary Results" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-12 px-6">
        <div className="max-w-5xl mx-auto">

          {/* Header */}
          <div className="text-center mb-12">
            <Header />

            <div className="bg-white/80 backdrop-blur-lg rounded-3xl p-8 border border-indigo-100 shadow-lg mt-6">
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                "{results.keyword}" 검색 결과
              </h1>
              <p className="text-indigo-600">
                총 {results.results?.length || 0}개의 뉴스 그룹
              </p>
            </div>
          </div>

          {/* Results */}
          <div className="space-y-8">
            {results.results && results.results.map((cluster, index) => (
              <div
                key={index}
                className="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300"
              >
                {/* Cluster Header */}
                <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 p-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-white">
                      그룹 {cluster.cluster_id + 1}
                    </h2>
                    <span className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold">
                      {cluster.size}개 기사
                    </span>
                  </div>
                </div>

                {/* Cluster Content */}
                <div className="p-8">
                  {/* Representative Article */}
                  <div className="mb-6">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="text-3xl">📰</div>
                      <div className="flex-1">
                        <a
                          href={cluster.representative_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xl font-bold text-gray-800 hover:text-purple-600 transition-colors"
                        >
                          {cluster.representative_title}
                        </a>
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="text-2xl">📝</div>
                        <h4 className="font-semibold text-gray-700 text-lg">AI 요약</h4>
                      </div>
                      <p className="text-gray-700 leading-relaxed">
                        {cluster.summary}
                      </p>
                    </div>
                  </div>

                  {/* Related Articles */}
                  {cluster.related_articles && cluster.related_articles.length > 0 && (
                    <div>
                      <div className="flex items-center gap-2 mb-4">
                        <div className="text-2xl">🔗</div>
                        <h4 className="font-semibold text-gray-700 text-lg">
                          관련 기사 ({cluster.related_articles.length}개)
                        </h4>
                      </div>
                      <ul className="space-y-3">
                        {cluster.related_articles.map((article, idx) => (
                          <li
                            key={idx}
                            className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                          >
                            <span className="text-purple-600 font-semibold flex-shrink-0">
                              {idx + 1}.
                            </span>
                            <a
                              href={article.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-gray-700 hover:text-purple-600 transition-colors"
                            >
                              {article.title}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="text-center mt-12">
            <button
              onClick={() => router.push('/')}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-xl transition-all"
            >
              새로운 검색하기
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
