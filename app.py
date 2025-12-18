import streamlit as st 
import time
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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

options = st.segmented_control(
    "",
    options=list(option_icons.keys()),
    format_func = lambda x : option_icons[x],
    label_visibility = "collapsed",
    selection_mode = "multi",
)




