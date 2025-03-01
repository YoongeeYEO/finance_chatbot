import gradio as gr

def chat_response(message, history):
    """
    사용자의 메시지와 대화 이력을 받아서 주식 분석 리포트를 생성하고 반환합니다.
    """
    # 사용자의 입력을 파싱하여 종목 심볼과 이름을 추출
    try:
        stock_symbol, stock_name = message.split(',')
        stock_symbol = stock_symbol.strip()
        stock_name = stock_name.strip()
    except ValueError:
        return "입력 형식이 올바르지 않습니다. '종목코드, 종목명' 형식으로 입력해 주세요."

    # 리포트 생성
    report = generate_report(stock_symbol, stock_name)
    return report

# Gradio ChatInterface 정의
chatbot = gr.ChatInterface(
    fn=chat_response,
    title="애널리스트 AI 챗봇",
    description="주식 종목 코드를 입력하면 해당 종목에 대한 분석 리포트를 제공합니다. 예시 입력: 'AAPL, Apple Inc.'"
)

# 인터페이스 실행
chatbot.launch()