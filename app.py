import streamlit as st 
import time
from openai import OpenAI
#from selenium import webdriver
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import NoSuchElementException
#from selenium.webdriver.common.by import By

import random




st.markdown("""
<style>
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html = True)
st.title("AI NEWS SUMMARY")
for i in range(3):
    st.markdown("##") 
query = st.text_input(
    "Enter search keyword:", ""
)
if st.button("Search"):
    '''Buffering'''
    
    '''progress = st.progress(0)
    status = st.empty()
    
    results = news_summarizer(query)
    summarized = []
    for i,r in enumerate(results):
        summarized.append(r)
        summarized.progress((i+1)/len(results))
        status.write(f"result complete {i+1}/{len(results)}")
    status.success("Complete")
    
    for r in summarized : st.write(r)
    '''

    
    time.sleep(2)
    
    
    keyword = query
    #driver.find_element(By.ID).send_keys(keyword)
    
    
    
option_icons = {
    "Search" : ":material/language: Search",
    "Deep resarch": ":material/biotech: Deep research",
    
}

st.set_page_config(page_title="ANS", layout="centered")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'>A N S</h1>", unsafe_allow_html=True)

#query = st.text_input("", placeholder="Search news…")

#st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
#search = st.button("🔍 Search")
#st.markdown("</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    query = st.text_input("Keyword", placeholder="AI, economy, stocks…")

with col2:
    source = st.selectbox("Source", ["Naver", "Google"])

with col3:
    limit = st.selectbox("Results", [5, 10, 20])

st.button("Search", use_container_width=True)

if search and query:
    st.switch_page("pages/news.py")




