import streamlit as st

st.set_page_config(page_title="News Articles", layout="wide")

# Custom CSS for card styling
st.markdown("""
<style>
    .news-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .news-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 10px;
    }
    .news-text {
        color: #4b5563;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .news-link {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }
    .news-link:hover {
        text-decoration: underline;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 📰 News Articles")

# Check if we have results
if 'results' not in st.session_state or not st.session_state.results:
    st.warning("⚠️ No search results found. Please go back and search first.")
    if st.button("← Back to Search"):
        st.switch_page("app.py")
    st.stop()

results = st.session_state.results

# Top stats
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="stat-box">
        <h2>{results['total']}</h2>
        <p>Articles Found</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-box">
        <h2>{results['query']}</h2>
        <p>Search Query</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    if st.button("🔍 New Search", type="primary", use_container_width=True):
        st.switch_page("app.py")

st.divider()

# Display articles in card layout
for idx, (article, text) in enumerate(zip(results['articles'], results['texts']), 1):
    # Create card container
    with st.container():
        st.markdown(f"""
        <div class="news-card">
            <div class="news-title">
                {idx}. {article.get('title', 'No title')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Article content in columns
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            # Text preview
            preview = text[:300] + "..." if len(text) > 300 else text
            st.markdown(f'<div class="news-text">{preview}</div>', unsafe_allow_html=True)
            
            # Read more expander
            with st.expander("📖 Read Full Article"):
                st.text_area(
                    "Full Text",
                    text,
                    height=300,
                    key=f"text_{idx}",
                    label_visibility="collapsed"
                )
        
        with col_b:
            # Article metadata
            st.markdown("**📊 Article Info**")
            st.caption(f"📏 {len(text)} characters")
            st.caption(f"📝 ~{len(text.split())} words")
            
            # Link to original
            if article.get('url'):
                st.markdown(f'<a href="{article["url"]}" target="_blank" class="news-link">🔗 Read Original</a>', unsafe_allow_html=True)
            
            # Action buttons
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✨ Summarize", key=f"sum_{idx}"):
                st.info("💡 Summarization coming soon!")
            
            if st.button("📥 Download", key=f"dl_{idx}"):
                st.download_button(
                    "Download Text",
                    text,
                    file_name=f"article_{idx}.txt",
                    key=f"download_{idx}"
                )
        
        st.divider()