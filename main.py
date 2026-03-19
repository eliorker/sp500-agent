import yfinance as yf
import pandas as pd
import requests

SYMBOL = "SPY"

def get_price_data():
    data = yf.download(SYMBOL, period="6mo", interval="1d")
    data["MA50"] = data["Close"].rolling(50).mean()
    data["MA200"] = data["Close"].rolling(200).mean()
    return data

def calculate_trend_score(data):
    latest = data.iloc[-1]

    price = float(latest["Close"])
    ma50 = float(latest["MA50"])
    ma200 = float(latest["MA200"])

    score = 0

    if price > ma200:
        score += 0.6
    else:
        score -= 0.4

    if price > ma50:
        score += 0.4
    else:
        score -= 0.2

    return max(-1, min(1, score))


NEWS_API_KEY = "59716da7-41da-4ccc-b395-597165b2be6d"

def get_news_sentiment():
    url = f"https://newsapi.org/v2/everything?q=SP500 OR stocks OR market&language=en&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()

    articles = r.get("articles", [])[:10]

    positive_words = ["rise", "gain", "record", "growth", "bull", "rally"]
    negative_words = ["fall", "drop", "recession", "crash", "inflation"]

    score = 0

    for a in articles:
        text = (a["title"] + " " + (a["description"] or "")).lower()

        for w in positive_words:
            if w in text:
                score += 0.1

        for w in negative_words:
            if w in text:
                score -= 0.1

    return max(-1, min(1, score))



def get_macro_score():
    # גרסה פשוטה (אפשר לשדרג אחר כך עם Fed data)
    return 0.2  # ברירת מחדל ניטרלית קלה   


def decision_engine(trend, sentiment, macro):
    final_score = (0.5 * trend) + (0.3 * sentiment) + (0.2 * macro)

    if final_score > 0.5:
        decision = "🟢 חיובי לטווח ארוך"
    elif final_score > 0:
        decision = "🟡 ניטרלי / זהיר"
    else:
        decision = "🔴 שלילי / הימנעות"

    return final_score, decision



TELEGRAM_TOKEN = "8642525638:AAEwLWrHt7ihHdZJhS3APN6iNfxOjZ1aAEo"
CHAT_ID = 8642525638
"""
def send_telegram(message):
    url = f"https://api.telegram.org/bot8642525638:AAEwLWrHt7ihHdZJhS3APN6iNfxOjZ1aAEo/sendMessage"
    requests.post(url, data={
        "chat_id": 8642525638,
        "text": message
    })

"""

def send_telegram(message):
    token = "8642525638:AAEwLWrHt7ihHdZJhS3APN6iNfxOjZ1aAEo"
    chat_id = 8642525638

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })

    print(response.text)

def run_agent():
    data = get_price_data()

    trend = calculate_trend_score(data)
    sentiment = get_news_sentiment()
    macro = get_macro_score()

    score, decision = decision_engine(trend, sentiment, macro)

    message = f"""
🧠 S&P500 AI Agent

📊 Trend score: {trend:.2f}
📰 News sentiment: {sentiment:.2f}
🌍 Macro: {macro:.2f}

📌 Final score: {score:.2f}

{decision}
"""

    send_telegram(message)

if __name__ == "__main__":
    run_agent()
