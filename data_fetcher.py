import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from langchain import OpenAI, VectorDBQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import json
from alpha_vantage.timeseries import TimeSeries
import openai
from langchain import OpenAI, LLMChain, PromptTemplate

# 1. 주가 데이터 import
def get_stock_data(symbol):
    """
    Alpha Vantage를 사용하여 주어진 종목의 일일 주가 데이터를 가져옵니다.
    """
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    return data

# 2. 실시간 뉴스 데이터 수집
def get_news_data(query, max_results=5):
    """
    Google Custom Search API를 사용하여 주어진 쿼리에 대한 뉴스를 가져옵니다.
    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}&num={max_results}&hl=ko&gl=kr"
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json().get('items', [])
        articles = []
        for result in search_results:
            article = {
                'title': result.get('title'),
                'link': result.get('link'),
                'description': result.get('snippet')
            }
            articles.append(article)
        return articles
    else:
        print("Error:", response.status_code, response.text)
        return []
    
# 3. 데이터 저장 및 전처리
def save_news_to_txt(articles, filename="news.txt"):
    """
    뉴스 기사 목록을 텍스트 파일로 저장합니다.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        for article in articles:
            title = article['title']
            description = article['description']
            link = article['link']
            file.write(f"Title: {title}\n")
            file.write(f"Description: {description}\n")
            file.write(f"Link: {link}\n\n")