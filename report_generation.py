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

def generate_report(stock_symbol, stock_name):
    """
    주어진 종목 심볼과 이름을 기반으로 주식 분석 리포트를 생성합니다.
    """
    # 주가 데이터 가져오기
    stock_data = get_stock_data(stock_symbol)
    latest_close = stock_data['4. close'][-1] if not stock_data.empty else 'N/A'
    latest_close_date = stock_data.index[-1].strftime('%Y-%m-%d') if not stock_data.empty else 'N/A'

    # 뉴스 데이터 가져오기
    news_articles = get_news_data(stock_name)

    # 데이터 저장
    save_news_to_txt(news_articles)

    # 프롬프트 생성
    prompt_template = """
    당신은 증권사에서 근무하는 애널리스트이다. 프롬프트에서 입력받은 주식 종목에 대해 증권사에서 실제 생산하는 리포트 형태로 A4 1장 정도 분량으로 아래 개요를 따라서 상세한 분석 리포트를 만들어줘.
    "6. 결론 및 투자의견" 부분에 반드시 계산한 목표주가를 포함하여 매수/중립/매도 중 하나의 의견을 선택해서 답변할것.
    "7. References" 부분에 참고한 자료들의 목록을 리스트하여 작성할것.

    1. 종목개요
    2. 시장 동향 및 주요 뉴스
    3. 재무 분석
    4. 기술적 분석
    5. 리스크 요인
    6. 결론 및 투자 의견
    7. References

    종목명: {stock_name}
    종목코드: {stock_symbol}

    최신 종가: {latest_close} USD (기준일: {latest_close_date})

    관련 뉴스:
    {news_info}

    위의 정보를 바탕으로 {stock_name}에 대한 종합적인 분석과 향후 전망을 포함한 분석 리포트를 작성해 주세요.
    """
    # Create a PromptTemplate instance
    prompt = PromptTemplate(
        input_variables=["stock_name", "stock_symbol", "latest_close", "latest_close_date", "news_info"],
        template=prompt_template,
    )


    news_info = ""
    for article in news_articles:
        title = article['title']
        link = article['link']
        news_info += f"- {title} ({link})\n"

    # LangChain을 사용하여 리포트 생성
    llm = OpenAI(model="gpt-4o", temperature=0.7)
    # Use ChatCompletion instead of Completion for chat models
    from langchain.chat_models import ChatOpenAI
    chat_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)  # Use gpt-4 for chat

    # Pass the prompt directly to the LLMChain instead of using a PromptTemplate
    chain = LLMChain(llm=chat_llm, prompt=prompt) # Change llm to chat_llm
    # Call run with an empty dictionary to satisfy the input requirement
    report = chain.run({
        "stock_name": stock_name,
        "stock_symbol": stock_symbol,
        "latest_close": latest_close,
        "latest_close_date": latest_close_date,
        "news_info": news_info
    })
    return report