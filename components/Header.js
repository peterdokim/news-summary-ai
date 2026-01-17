import Link from 'next/link';

export default function Header() {
  return (
    <Link href="/">
      <div className="text-center mb-8 transform hover:scale-105 transition-transform duration-500 cursor-pointer">
        {/*<div className="mb-3">
          <div className="inline-block p-3 bg-white/60 backdrop-blur-lg rounded-2xl shadow-lg">
            <div className="text-4xl">📰</div>
          </div>
        </div> */}
        <h1 className="text-4xl font-black text-gray-800 mb-3 tracking-widest drop-shadow-lg animate-fade-in">
          A N S
        </h1>
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="h-0.5 w-8 bg-gradient-to-r from-transparent via-indigo-400 to-transparent"></div>
          <p className="text-lg text-indigo-700 font-light tracking-wide">
            AI News Summarizer
          </p>
          <div className="h-0.5 w-8 bg-gradient-to-r from-transparent via-indigo-400 to-transparent"></div>
        </div>
        <p className="text-gray-600 text-xs">
          Powered by OpenAI • 실시간 뉴스 분석
        </p>
      </div>
    </Link>
  );
}
