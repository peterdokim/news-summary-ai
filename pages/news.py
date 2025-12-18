import streamlit as st

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Search Results",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

toggle = st.toggle("🌗 Dark mode", value=st.session_state.theme == "dark")
st.session_state.theme = "dark" if toggle else "light"

# ---------- THEMES ----------
LIGHT_THEME = """
<style>
.stApp { background-color: #f7f9fc; color: #111; }
.card {
    background: white;
    padding: 1.2rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}
</style>
"""

DARK_THEME = """
<style>
.stApp { background-color: #0e1117; color: #fafafa; }
.card {
    background: #1c1f26;
    padding: 1.2rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    margin-bottom: 1rem;
}
</style>
"""
st.markdown(DARK_THEME if st.session_state.theme == "dark" else LIGHT_THEME,
            unsafe_allow_html=True)

# ================= DUMMY DATA =================
dummy_articles = [
    {
        "title": "AI Transforms News Summarization in 2025",
        "summary": "Artificial intelligence is increasingly being used to summarize news articles faster and more accurately.",
        "source": "Tech Daily",
        "date": "2025-01-12"
    },
    {
        "title": "South Korea Invests Billions in AI Research",
        "summary": "The government announced a major investment plan to boost AI research and talent development.",
        "source": "Korea Herald",
        "date": "2025-01-10"
    },
    {
        "title": "Generative AI Changes Journalism",
        "summary": "Media companies are adopting generative AI tools to assist reporters and editors.",
        "source": "Reuters",
        "date": "2025-01-09"
    },
    {
        "title": "AI Ethics Becomes Global Priority",
        "summary": "Countries and tech companies are working together to establish ethical AI guidelines.",
        "source": "BBC News",
        "date": "2025-01-08"
    }
]

# ================= STYLES =================
st.markdown("""
<style>
.card {
    background-color: #1f2933;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.45);
}
.card-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.card-summary {
    font-size: 0.95rem;
    color: #d1d5db;
    margin-bottom: 14px;
}
.card-footer {
    font-size: 0.8rem;
    color: #9ca3af;
    display: flex;
    justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("## 📰 Search Results")
st.markdown("Showing sample articles (dummy data)")

# ================= CARD GRID =================
cols = st.columns(2)

for idx, article in enumerate(dummy_articles):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{article['title']}</div>
            <div class="card-summary">{article['summary']}</div>
            <div class="card-footer">
                <span>{article['source']}</span>
                <span>{article['date']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)