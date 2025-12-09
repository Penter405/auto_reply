# LINE Bot 客服機器人

基於 Python Flask 的 LINE Bot 客服機器人，部署於 Vercel。

## 功能

- 🔹 關鍵字自動回覆（服務時間、聯絡方式、價格等）
- 🔹 預設回覆訊息引導用戶

## 專案結構

```
LineBot/
├── api/
│   └── index.py          # Flask 應用程式
├── vercel.json           # Vercel 部署設定
├── requirements.txt      # Python 依賴套件
├── .env.example          # 環境變數範例
└── README.md
```

## 部署步驟

### 1. 設定 LINE Developers Console

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 取得 **Channel Secret** 和 **Channel Access Token**

### 2. 部署到 Vercel

1. 將專案推送到 GitHub
2. 在 [Vercel](https://vercel.com/) 建立新專案並連結 repository
3. 設定環境變數：
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
4. 部署完成後取得 URL

### 3. 設定 Webhook

1. 回到 LINE Developers Console
2. 在 Messaging API 設定中：
   - Webhook URL: `https://your-project.vercel.app/api/webhook`
   - 開啟 **Use webhook**
   - 關閉 **Auto-reply messages**（停用自動回覆）

## 客服關鍵字

| 關鍵字 | 回覆內容 |
|--------|---------|
| 服務時間 / 營業時間 | 營業時間資訊 |
| 聯絡方式 / 聯繫 | 聯絡資訊 |
| 價格 / 費用 | 價格說明 |
| 幫助 / help | 功能選單 |

## 本地開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
set LINE_CHANNEL_SECRET=your_secret
set LINE_CHANNEL_ACCESS_TOKEN=your_token

# 執行（需搭配 ngrok 進行測試）
python api/index.py
```
