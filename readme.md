# 🤖 AI News Summarizer

An intelligent news summarization application that scrapes articles from the web and generates concise summaries using Claude AI.

## 🎯 Overview

This application combines web scraping, AI-powered summarization, and an intuitive web interface to help users quickly digest news articles.

```
User Input → BeautifulSoup → Text Processing → Claude API → Streamlit Display
```

## 🏗️ Architecture

### Pipeline Components

#### 1. **Web Scraping Layer** (BeautifulSoup)
- Extracts article content from news URLs
- Parses HTML to identify headlines, body text, and metadata
- Handles multiple news source formats
- Implements robust error handling

#### 2. **AI Summarization Engine** (Claude API)
- Generates intelligent, context-aware summaries
- Configurable summary lengths (short/medium/long)
- Extracts key points and main ideas
- Preserves important facts and context

#### 3. **Web Interface** (Streamlit)
- Clean, user-friendly interface
- Real-time article processing
- Side-by-side original vs summary view
- Export functionality (TXT/PDF)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-news-summarizer.git
cd ai-news-summarizer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run app.py
```

### Requirements.txt

```
beautifulsoup4==4.12.2
requests==2.31.0
anthropic==0.25.0
streamlit==1.32.0
python-dotenv==1.0.0
```

## 📁 Project Structure

```
ai-news-summarizer/
│
├── app.py                 # Main Streamlit application
├── scraper.py            # BeautifulSoup scraping logic
├── summarizer.py         # Claude API integration
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
│
├── tests/               # Unit tests
│   ├── test_scraper.py
│   └── test_summarizer.py
│
└── examples/            # Example articles and outputs
    └── sample_output.txt
```

## 💻 Code Examples

### Scraping Module (scraper.py)

```python
import requests
from bs4 import BeautifulSoup

def scrape_article(url):
    """
    Scrapes article content from a given URL.
    
    Args:
        url (str): The URL of the news article
        
    Returns:
        dict: Contains 'title', 'content', and 'date'
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('h1').text.strip()
        
        # Find article body (adjust selectors based on target sites)
        article_body = soup.find('article') or soup.find('div', class_='article-body')
        content = article_body.get_text(strip=True)
        
        return {
            'title': title,
            'content': content,
            'url': url
        }
        
    except Exception as e:
        return {'error': str(e)}
```

### Summarization Module (summarizer.py)

```python
import anthropic
import os

def summarize_text(text, length="medium"):
    """
    Generates a summary of the given text using Claude API.
    
    Args:
        text (str): The article text to summarize
        length (str): 'short', 'medium', or 'long'
        
    Returns:
        str: The generated summary
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    length_prompts = {
        "short": "in 2-3 sentences",
        "medium": "in 1 paragraph",
        "long": "in 2-3 paragraphs"
    }
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Summarize this news article {length_prompts[length]}. Focus on the main points and key facts:\n\n{text}"
        }]
    )
    
    return message.content[0].text
```

### Main Application (app.py)

```python
import streamlit as st
from scraper import scrape_article
from summarizer import summarize_text

st.set_page_config(page_title="AI News Summarizer", page_icon="🤖")

st.title("🤖 AI News Summarizer")
st.write("Enter a news article URL to get an intelligent summary")

url = st.text_input("📰 Article URL:", placeholder="https://example.com/news/article")

col1, col2 = st.columns([1, 3])
with col1:
    length = st.selectbox("Summary Length:", ["short", "medium", "long"])

if st.button("✨ Summarize", type="primary"):
    if url:
        with st.spinner("🔍 Scraping article..."):
            article = scrape_article(url)
            
        if 'error' not in article:
            with st.spinner("🧠 Generating summary..."):
                summary = summarize_text(article['content'], length)
            
            st.success("✅ Summary generated!")
            
            st.subheader("📝 Summary")
            st.write(summary)
            
            with st.expander("📄 Original Article"):
                st.write(f"**{article['title']}**")
                st.write(article['content'][:500] + "...")
        else:
            st.error(f"❌ Error: {article['error']}")
    else:
        st.warning("⚠️ Please enter a URL")
```

## ✨ Features

- ✅ Multi-source news scraping
- ✅ Adjustable summary length (short/medium/long)
- ✅ Clean and intuitive UI
- ✅ Error handling and validation
- ✅ Side-by-side comparison
- 🔜 Keyword extraction
- 🔜 Sentiment analysis
- 🔜 Export to PDF/Markdown
- 🔜 Save favorite summaries

## 🛠️ Development Roadmap

### Phase 1: Core Functionality ✅
- [x] Basic web scraping
- [x] Claude API integration
- [x] Streamlit interface

### Phase 2: Enhanced Features 🚧
- [ ] Support for multiple news sources
- [ ] Batch processing
- [ ] Summary history

### Phase 3: Advanced Features 📋
- [ ] User accounts and preferences
- [ ] Custom summarization prompts
- [ ] RSS feed integration
- [ ] Chrome extension

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- [Anthropic Claude](https://www.anthropic.com/) for AI summarization
- [Streamlit](https://streamlit.io/) for the web framework

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/ai-news-summarizer](https://github.com/yourusername/ai-news-summarizer)

---

⭐ If you find this project useful, please consider giving it a star!
