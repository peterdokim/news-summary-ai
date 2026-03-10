# ANS - AI News Summarizer

AI-powered news summarization tool that crawls Naver news, clusters similar articles, and generates intelligent summaries using OpenAI GPT.

## 🎯 Overview

This application combines web scraping, AI-powered clustering, and intelligent summarization to help users quickly understand news trends.

```
Next.js Frontend → API Route → Flask Backend → News Crawler + OpenAI Embeddings + GPT Summarization
```

## 🏗️ Architecture

### Pipeline Components

#### 1. **Web Scraping Layer** (BeautifulSoup)
- Searches and extracts article content from Naver News
- Parses HTML to identify headlines and body text
- Handles multiple Naver news formats (general/sports/entertainment)
- Robust error handling for failed requests

#### 2. **AI Clustering Engine** (OpenAI + scikit-learn)
- Converts articles to embeddings using `text-embedding-3-small`
- Groups similar articles using KMeans clustering
- Identifies representative articles from each cluster
- Optimizes content organization

#### 3. **AI Summarization Engine** (OpenAI GPT-4o-mini)
- Generates concise 3-sentence summaries
- Context-aware and factual
- Korean language support
- Preserves key facts and main ideas

#### 4. **Modern Web Interface** (Next.js + Tailwind CSS)
- Beautiful, responsive UI with animations
- Real-time search and processing
- Clustered results view
- Related articles grouping

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd news-summary-ai

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

⚠️ **IMPORTANT**: Never commit your `.env` file to git!

### Running the Application

You need to run both servers:

**Terminal 1: Flask Backend**
```bash
python server.py
```

**Terminal 2: Next.js Frontend**
```bash
npm run dev
```

Then open http://localhost:3000 in your browser.

## 📁 Project Structure

```
news-summary-ai/
├── pages/
│   ├── index.js          # Home page with search form
│   ├── news.js           # Results page with clustered summaries
│   ├── _app.js           # Next.js app wrapper
│   └── api/
│       └── search.js     # API route handler
├── api/
│   └── news_summarizer.py # News crawler + AI clustering logic
├── styles/
│   └── globals.css       # Global styles with Tailwind
├── server.py             # Flask backend server
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
├── package.json          # Node dependencies
└── README.md             # This file
```

## 💻 How It Works

1. **User searches** for a keyword on the Next.js frontend
2. **Frontend API route** (`/api/search`) proxies the request to Flask backend
3. **Flask backend** receives the search request
4. **News Crawler** searches Naver and extracts article URLs
5. **Article Extractor** scrapes full content from each URL
6. **Embeddings** are generated using OpenAI `text-embedding-3-small`
7. **KMeans Clustering** groups similar articles together
8. **GPT-4o-mini** summarizes the representative article from each cluster
9. **Results** are sent back to frontend and displayed in a beautiful UI

## 🎨 Features

- 🔍 **Smart Search**: Keyword-based Naver news search
- 🤖 **AI Clustering**: Groups similar articles using embeddings
- 📝 **Intelligent Summaries**: 3-sentence summaries in Korean
- ⚡ **Real-time Processing**: Live search and summarization
- 🎯 **Cluster View**: See related articles grouped together
- 💎 **Modern UI**: Beautiful gradient design with Tailwind CSS
- 📱 **Responsive**: Works on all device sizes

## 🛠️ API Endpoints

### Flask Backend

- **POST** `/api/summarize` - Summarize news articles
  ```json
  {
    "keyword": "AI",
    "max_articles": 20,
    "n_clusters": 3
  }
  ```

- **GET** `/health` - Health check

### Next.js API Routes

- **POST** `/api/search` - Proxy to Flask backend

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `PYTHON_API_URL` | Flask backend URL | `http://localhost:5000` |
| `PORT` | Flask server port | `5000` |

## 🚨 Security Notes

🔒 **NEVER commit your `.env` file!**

If you accidentally exposed your API key:
1. Go to https://platform.openai.com/api-keys
2. Revoke the exposed key
3. Generate a new key
4. Update your `.env` file

## 🐛 Troubleshooting

### "Flask 서버에 연결할 수 없습니다"
- Ensure Flask server is running on port 5000
- Check `PYTHON_API_URL` in `.env`

### "OPENAI_API_KEY가 설정되지 않았습니다"
- Verify `.env` file exists in project root
- Check that the API key is valid

### No search results
- Check internet connection
- Try a different keyword
- Increase number of articles

## 🎯 Technologies Used

**Frontend:**
- Next.js 14
- React 18
- Tailwind CSS

**Backend:**
- Flask 3.0
- OpenAI API (GPT-4o-mini, text-embedding-3-small)
- BeautifulSoup4
- scikit-learn
- NumPy

## 📝 License

MIT

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📧 Contact

Built with ♥ by ANS Team

---

⭐ If you find this project useful, please consider giving it a star!
