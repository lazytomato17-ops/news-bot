import os
import time
import requests
import feedparser
import google.generativeai as genai

# ==========================================
# GitHubの「Secrets」からキーを読み込む設定
# （ここにはキーを直接書かないで！自動で読み込まれます）
# ==========================================
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


# 変更後（例：AUTOMATONにする場合）
RSS_URL = "https://automaton-media.com/feed/"

# 成功した最強モデル
MODEL_NAME = 'gemini-2.5-flash' 

# Gemini設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def get_sarcastic_summary(title):
        # 書き換え用コード
    prompt = f"""
    あなたは「冷静沈着なベテランゲーマー」です。
    以下のニュースタイトルを見て、
    「淡々とした口調」で、業界の裏読みや鋭い指摘を3行以内でしてください。
    
    ・感嘆符（！）や叫び声は禁止です。
    ・ネットスラングは使わず、知的に皮肉ってください。
    
    記事タイトル: {title}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"（Geminiのエラー: {e}）"

def main():
    print("🚀 起動しました")
    
    # ブロック回避用ヘッダー
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(RSS_URL, headers=headers, timeout=10)
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"RSSエラー: {e}")
        return

    if not feed.entries:
        print("記事なし")
        return

    final_message = "📢 **朝のゲームニュース** 🐔\n------------------------\n"
    
    # 最新3件
    for entry in feed.entries[:3]:
        summary = get_sarcastic_summary(entry.title)
        final_message += f"**{entry.title}**\n{summary}\n{entry.link}\n\n"
        time.sleep(1) # 連投制限への配慮

    # Discord送信
    requests.post(DISCORD_WEBHOOK_URL, json={"content": final_message})
    print("✅ 送信完了")

if __name__ == "__main__":
    main()
