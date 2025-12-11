from flask import Flask, request, abort
import os
import traceback

app = Flask(__name__)

# LINE Bot credentials
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')

# Pinecone credentials
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY', '')

# Customer service keyword responses (保留基本關鍵字)
CUSTOMER_SERVICE_RESPONSES = {
    '服務時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '營業時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '聯絡方式': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '聯繫': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '幫助': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 或直接輸入問題，我會用 AI 為您解答！',
    'help': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 或直接輸入問題，我會用 AI 為您解答！',
}


def ask_pinecone_rag(question: str) -> str:
    """Query Pinecone RAG assistant for answers."""
    try:
        from pinecone import Pinecone
        from pinecone_plugins.assistant.models.chat import Message
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        assistant = pc.assistant.Assistant(assistant_name="autoreply")
        
        msg = Message(content=question)
        resp = assistant.chat(messages=[msg])
        
        return resp["message"]["content"]
    except Exception as e:
        print(f"")
        return f"Pinecone RAG Error: {str(e)}"


def get_response(user_message: str) -> str:
    """Get appropriate response based on user message."""
    # 先檢查關鍵字
    for keyword, response in CUSTOMER_SERVICE_RESPONSES.items():
        if keyword in user_message:
            return response
    
    # 沒有符合關鍵字，使用 Pinecone RAG
    return ask_pinecone_rag(user_message)


# Health check endpoint
@app.route('/', methods=['GET'])
def index():
    return 'LINE Bot with Pinecone RAG is running!'


@app.route('/api/webhook', methods=['GET'])
def webhook_get():
    return 'Webhook endpoint is ready. Use POST for LINE webhook.'


@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle LINE webhook requests."""
    try:
        # Optional: we don't rely on SDK for signature verification here
        import hmac
        import hashlib
        import base64
        from linebot.v3.messaging import (
            Configuration,
            ApiClient,
            MessagingApi,
            ReplyMessageRequest,
            TextMessage
        )
        import json
        
        signature = request.headers.get('X-Line-Signature', '')
        # use raw bytes for signature verification
        body_bytes = request.get_data()
        try:
            body = body_bytes.decode('utf-8')
        except Exception:
            body = ''

        # Verify signature if channel secret is set
        if LINE_CHANNEL_SECRET:
            try:
                hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body_bytes, hashlib.sha256).digest()
                computed_signature = base64.b64encode(hash).decode()
                if not hmac.compare_digest(computed_signature, signature):
                    print('Invalid LINE signature')
                    abort(400)
            except Exception as e:
                print(f'Signature verification error: {e}')
                abort(400)
        
        try:
            events = json.loads(body).get('events', [])
        except:
            return 'OK'
        
        configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        
        for event in events:
            if event.get('type') == 'message' and event.get('message', {}).get('type') == 'text':
                reply_token = event.get('replyToken')
                user_message = event.get('message', {}).get('text', '')
                response_text = get_response(user_message)
                
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=reply_token,
                            messages=[TextMessage(text=response_text)]
                        )
                    )
        
        return 'OK'
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return 'OK'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
