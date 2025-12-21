import streamlit as st 
import time
from openai import OpenAI
from news_summarizer import NewsSummarizer
import os
from dotenv import load_dotenv


st.set_page_config(page_title="ANS", layout="centered")

if 'results' not in st.session_state:
    st.session_state.results = None

if 'summarizer' not in st.session_state:
    st.session_state.summarizer = None

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>A N S</h1>", unsafe_allow_html=True)

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ Please create .env file with OPENAI_API_KEY=sk-xxx")
    st.stop()
    
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    query = st.text_input("Keyword", placeholder="AI, economy, stocks…")

with col2:
    source = st.selectbox("Source", ["Naver", "Google"])

with col3:
    limit = st.selectbox("Results", [5, 10, 20])

searched = st.button("Search", use_container_width=True)


if searched:
    if not query :
        st.warning("Please enter a keyword")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error ("set your api key with the env")
    else:
        try:
            if st.session_state.summarizer is None:
                with st.spinner('....'):
                    st.session_state.summarizer = NewsSummarizer()
            summarizer = st.session_state.summarizer
            # loading animation and pop up intended
            with st.spinner(f'Search Naver for query'):
                articles = summarizer.crawl_news(keyword=query,max_articles=limit)
                
            st.info(f"articles")
            
            if articles:
                with st.spinner('Process articles'):
                    valid_articles, texts = summarizer.prepare_articles_for_embedding(articles)
                    
                if valid_articles:
                    st.session_state.results = {
                        'success' : True,
                        'query' : query,
                        'articles' : valid_articles,
                        'texts' : texts,
                        'total' : len(valid_articles),
                        'failed' : len(articles) - len(valid_articles)
                    }
                    st.success(f" Found {len(valid_articles)} articles!")
                    st.info("🔄 Redirecting to news page...")
                    st.switch_page("pages/news.py")
                else:
                    st.session_state.results = {
                        'success' : False,
                        'error' : f'All'
                    } 
        except ValueError as e:
            st.error(f"Config error")
            st.session_state.summarizer = None
        
        except Exception as e:
            st.error(f"error")
            import traceback
            
            with st.expander("Debug info"):
                st.code(traceback.format_exc())
            st.session_state.results = {
                'success' : False,
                'error' : str(e)
            }

#if st.session_state.results:
   # results = st.session_state.results
    
    #if results['success']:
     #   st.success(f"Processed")
        
     #   if results.get('failed',0) > 0:
      #      st.warning(f"articles failed to extract")
            
     #   st.divider()
        
      #  for idx, (article,text) in enumerate(zip(results['articles'], results['texts']),1):
       #     with st.expander(
        #        f"Article : {article.get('title','No title')}"
       #     ):
                
          #      st.subheader(article.get('title','No title'))
                
         #       if article.get('url'):
          #          st.markdown(f"🔗 [Read Original Article]({article['url']})")
                    
          #      st.divider()
                
           #     st.markdown("### Text for Enbedding")
                
             #   st.text_area(
             #      "Article Content",
             #       text,
              #      height=300,
             #       key=f"text_{idx}",
             #       label_visibility = "collapsed"
             #   )
             #   col_a, col_b = st.columns(2)
             #   with col_a:
             ##       st.caption(f"📏 Length: {len(text)} characters")
             #   with col_b:
             #       st.caption(f"📝 Words: ~{len(text.split())} words")
                    
                    
