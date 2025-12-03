import os
import time
import requests
import feedparser
import google.generativeai as genai

# ==========================================
# 設定エリア
# ==========================================
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# ニュースサイト (AUTOMATON)
RSS_URL = "https://automaton-media.com/feed/"
# モデル
MODEL_NAME = 'gemini-2.5-flash' 

# Gemini設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

def get_quiet_summary(title):
    # ★修正：うるさくない「冷静な」プロンプトにしました
    prompt = f"""
    あなたは「冷静沈着なベテランゲーマー」です。
    以下のニュースタイトルを見て、
    「淡々とした口調」で、業界の裏読みや鋭い指摘を3行以内でしてください。
    
    ・感嘆符（！）や叫び声は禁止です。
    ・ネットスラングは控えめに、知的に皮肉ってください。
    
    記事タイトル: {title}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"（AI生成エラー）"

def fetch_rss_robust():
    """RSS取得を3回までリトライする粘り強い関数"""
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for i in range(3): # 3回挑戦する
        try:
            print(f"📡 接続トライ {i+1}回目...")
            # timeoutを30秒に延長
            resp = requests.get(RSS_URL, headers=headers, timeout=30)
            feed = feedparser.parse(resp.content)
            
            if feed.entries:
                return feed
            else:
                print("記事が空でした。リトライします。")
        
        except Exception as e:
            print(f"⚠️ エラー発生: {e}")
        
        # 失敗したら10秒待ってから次へ
        time.sleep(10)
    
    return None # 3回やってもダメなら諦める

def main():
    print("🚀 起動しました")
    
    # 強化版の取得関数を使う
    feed = fetch_rss_robust()

    if not feed:
        print("❌ 3回試しましたが、記事が取れませんでした。")
        return

    final_message = "🎮 **朝のゲームニュース** ☕\n------------------------\n"
    
    # 最新3件
    for entry in feed.entries[:3]:
        summary = get_quiet_summary(entry.title)
        final_message += f"**{entry.title}**\n{summary}\n{entry.link}\n\n"
        time.sleep(2) 

    # Discord送信
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": final_message})
        print("✅ 送信完了")
    except Exception as e:
        print(f"Discord送信エラー: {e}")

if __name__ == "__main__":
    main()
