from flask import Flask, request, abort
import os
import traceback

app = Flask(__name__)

# LINE Bot credentials from environment variables
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')

# Customer service keyword responses
CUSTOMER_SERVICE_RESPONSES = {
    '服務時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '營業時間': '🕐 我們的服務時間：\n週一至週五：09:00 - 18:00\n週六：10:00 - 16:00\n週日及國定假日休息',
    '聯絡方式': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '聯繫': '📞 聯絡我們：\n電話：02-1234-5678\nEmail：service@example.com\n地址：台北市信義區xxx路xx號',
    '價格': '💰 價格資訊：\n請參考我們的官網價格頁面，或來電洽詢專人為您報價。\n官網：https://example.com/pricing',
    '費用': '💰 價格資訊：\n請參考我們的官網價格頁面，或來電洽詢專人為您報價。\n官網：https://example.com/pricing',
    '幫助': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 輸入「價格」了解價格資訊\n\n如需其他協助，請直接描述您的問題！',
    'help': '📋 您好！我可以幫您處理以下問題：\n\n🔹 輸入「服務時間」查詢營業時間\n🔹 輸入「聯絡方式」取得聯絡資訊\n🔹 輸入「價格」了解價格資訊\n\n如需其他協助，請直接描述您的問題！',
}

DEFAULT_RESPONSE = '感謝您的訊息！\n\n如需快速查詢，您可以輸入以下關鍵字：\n🔹 服務時間\n🔹 聯絡方式\n🔹 價格\n🔹 幫助\n\n或稍候將有專人為您服務。'


def get_response(user_message: str) -> str:
    """Get appropriate response based on user message."""
    for keyword, response in CUSTOMER_SERVICE_RESPONSES.items():
        if keyword in user_message:
            return response
    return DEFAULT_RESPONSE


# Health check endpoint
@app.route('/', methods=['GET'])
def index():
    return 'LINE Bot is running!'


@app.route('/api/webhook', methods=['GET'])
def webhook_get():
    return 'Webhook endpoint is ready. Use POST for LINE webhook.'


@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle LINE webhook requests."""
    try:
        from linebot.v3 import WebhookHandler
        from linebot.v3.exceptions import InvalidSignatureError
        from linebot.v3.messaging import (
            Configuration,
            ApiClient,
            MessagingApi,
            ReplyMessageRequest,
            TextMessage
        )
        from linebot.v3.webhooks import MessageEvent, TextMessageContent
        import json
        
        signature = request.headers.get('X-Line-Signature', '')
        body = request.get_data(as_text=True)
        
        # Verify signature
        handler = WebhookHandler(LINE_CHANNEL_SECRET)
        
        try:
            events = json.loads(body).get('events', [])
        except:
            return 'OK'
        
        # Process events
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


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
