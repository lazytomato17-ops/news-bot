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
    prompt = f"""
    あなたは「辛口な古参ゲーマー（またはアニオタ）」です。
    以下のニュースタイトルを見て、
    「ゲーマー視点の皮肉や、オタク特有の早口なノリ」で3行以内でコメントしてください。
    感嘆符（！）やネットスラングを使ってもいいです。呪術廻戦ネタを使ってもいいです。
    
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

    final_message = "📢 **朝の辛口Zennニュース** 🐔\n------------------------\n"
    
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
