from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time
import numpy as np
import pandas as pd
import os
import random

from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-summarization")
model = BartForConditionalGeneration.from_pretrained("gogamza/kobart-summarization")

# 찾는 CSS가 없으면 return False
def check_exists_by_selector(driver, selector):
    try:
        driver.find_element(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return False
    return True

# TODO: max_articles 갯수가 첫 페이지 뉴스 갯수 이상이면 다음 페이지로 넘어가기
def crawl_news(keyword: str, max_articles: int=5):
    driver = webdriver.Chrome()
    driver.get(f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={keyword}")

    data_dict = {'title' : [], 'date' : [], 'reporter' : [], 'content' : []}
    
    box = driver.find_element(By.CLASS_NAME, 'group_news')
    lists = box.find_elements(By.LINK_TEXT,'네이버뉴스')
    lists = lists[:max_articles]


    for li in lists:
        actions = ActionChains(driver).move_to_element(li)
        actions.perform()

        # 클릭시 새로운 탭으로 전환 (window: Keys.CONTROL, Mac: Keys.COMMAND)
        li.send_keys(Keys.COMMAND + '\n')
        driver.switch_to.window(driver.window_handles[-1])
        driver.implicitly_wait(3)

        title = driver.find_element(By.CSS_SELECTOR, '#ct > div.media_end_head.go_trans > div.media_end_head_title').text.strip()
        data_dict['title'].append(title)
        date = driver.find_element(By.CSS_SELECTOR, '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div > div.media_end_head_info_datestamp > div > div > div:nth-child(1) > span').text.strip()
        data_dict['date'].append(date)
        if check_exists_by_selector(driver, '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div > div.media_end_head_journalist_name_area'):
            reporter = driver.find_element(By.CSS_SELECTOR, '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_journalist > div > div.media_end_head_journalist_name_area').text.strip()
        else:
            reporter = ''
        data_dict['reporter'].append(reporter)
        content = driver.find_element(By.CSS_SELECTOR, '#contents').text.strip()
        data_dict['content'].append(content)

        driver.close()
        driver.switch_to.window(driver.window_handles[0]) 
    
    driver.quit()
    return data_dict

def _raw_summarize(text: str, max_length: int = 128, min_length: int = 20) -> str:
    inputs = tokenizer(
        [text],
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    )

    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=2,
        max_length=max_length,
        min_length=min_length,
        early_stopping=True,
        no_repeat_ngram_size=3
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize_article(text: str) -> str:
    prompt = (
        "다음은 하나의 한국어 뉴스 기사 본문입니다. "
        "핵심 사실과 내용을 중심으로 2~3문장으로 간단히 요약해 주세요.\n\n"
        + text
    )
    return _raw_summarize(prompt, max_length=128, min_length=20)

def summarize_articles(contents: list[str]) -> str:
    partial_summaries = [summarize_article(c) for c in contents]
    combined_text = "\n\n".join(partial_summaries)

    combined_text = "\n\n".join(f"- {s}" for s in partial_summaries)

    final_prompt = (
        "다음은 서로 관련된 여러 뉴스 기사의 요약들입니다.\n"
        "중복되는 내용을 묶고, 전체 흐름을 하나의 기사처럼 정리해서 "
        "핵심만 3~4문장으로 한국어로 요약해 주세요.\n\n"
        + combined_text
    )

    final_summary = _raw_summarize(final_prompt, max_length=96, min_length=24)
    return final_summary

if __name__ == "__main__":  
    keyword = input("검색어를 입력하세요: ")
    data_dict = crawl_news(keyword, max_articles=5)
    final_summary = summarize_articles(data_dict['content'])

    print("\n[최종 종합 요약]")
    print(final_summary)