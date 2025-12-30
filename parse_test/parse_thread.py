import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import re
import time

# ================= 設定區 =================
# 目標 Threads 文章網址 (支援 threads.com 自動修正)
target_url = "https://www.threads.com/@bnext_official/post/DDtEjRyvizl?hl=zh-tw"
output_folder = r"json_test/Threads"
os.makedirs(output_folder, exist_ok=True)

# 【請填入你的 Threads Cookie】(與 Dcard 類似，由 F12 -> Network -> Request Headers 取得)
# 務必包含 "sessionid" 或 "datr" 等關鍵欄位
MY_COOKIE = 'mid=aNAfOwALAAHjAid1htZC3NvZZHFG; datr=yoHfaAZKpm3TO4paLAfRU4WO; ig_did=C13E577B-4C87-4235-92E9-23E86D9CB452; ds_user_id=38965707; ps_n=1' 
# ==========================================

def clean_filename(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)

def parse_threads_post(url):
    # 1. 網址修正 (threads.com -> threads.net)
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
        print(f"網址已自動修正為: {url}")

    # 2. 準備請求 (偽裝成瀏覽器)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.threads.net/",
        "Cookie": MY_COOKIE,
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        print("正在連線至 Threads...")
        resp = requests.get(url, headers=headers)
        
        if resp.status_code != 200:
            print(f"❌ 抓取失敗: {resp.status_code}")
            print("請檢查 Cookie 是否已過期，或是否為私人帳號。")
            return None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # === 核心解析邏輯 ===
        article_data = {}
        
        # 方法 A: 嘗試尋找 LD-JSON (這是最完美的資料源)
        # Threads 通常會把文章資料包在一個 <script type="application/ld+json"> 裡面
        json_scripts = soup.find_all("script", type="application/ld+json")
        ld_json = None
        
        for script in json_scripts:
            try:
                data = json.loads(script.get_text())
                # 判斷是不是文章資料 (通常會有 'articleBody' 或 'headline')
                if "articleBody" in data or "headline" in data:
                    ld_json = data
                    break
            except:
                continue

        if ld_json:
            print("✅ 成功找到 LD-JSON 結構化資料！")
            # 解析 LD-JSON
            article_data["article_title"] = ld_json.get("headline", "無標題")
            article_data["content_raw"] = ld_json.get("articleBody", "")
            
            # 作者處理
            author_info = ld_json.get("author", {})
            if isinstance(author_info, list) and len(author_info) > 0:
                 article_data["article_author"] = author_info[0].get("name", "Unknown")
            elif isinstance(author_info, dict):
                 article_data["article_author"] = author_info.get("name", "Unknown")
            else:
                 article_data["article_author"] = "Unknown"
                 
            # 時間處理 (Threads 的 LD-JSON 時間通常是 ISO 格式)
            pub_time_str = ld_json.get("datePublished", "")
            if pub_time_str:
                try:
                    dt = datetime.datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
                    # 轉台灣時間
                    dt_tw = dt.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                    article_data["publish_time"] = dt_tw.strftime("%Y-%m-%d %H:%M:%S")
                    article_data["date_year"] = dt_tw.year
                    article_data["date_month"] = dt_tw.month
                    article_data["date_day"] = dt_tw.day
                except:
                    article_data["publish_time"] = str(datetime.datetime.now())
        
        else:
            print("⚠️ 找不到 LD-JSON，改用 Meta Tags 解析 (備案)...")
            # 方法 B: Meta Tags (備案)
            # 標題通常在 og:title，內文在 og:description
            og_title = soup.find("meta", property="og:title")
            og_desc = soup.find("meta", property="og:description")
            
            # og:title 格式通常是 "姓名 on Threads: \"內文前幾字...\""
            # og:description 通常就是內文
            
            raw_title = og_title["content"] if og_title else "無標題"
            raw_desc = og_desc["content"] if og_desc else ""
            
            # 嘗試從標題切出作者
            if " on Threads" in raw_title:
                author = raw_title.split(" on Threads")[0]
            else:
                author = "Unknown"
            
            article_data["article_title"] = f"Threads Post by {author}"
            article_data["article_author"] = author
            article_data["content_raw"] = raw_desc
            
            # Meta Tag 很難抓到精確時間，先用當下時間代替
            now = datetime.datetime.now()
            article_data["publish_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            article_data["date_year"] = now.year
            article_data["date_month"] = now.month
            article_data["date_day"] = now.day

        # === 統一補齊 PTT JSON 欄位 ===
        article_data["article_source"] = "Threads"
        article_data["article_url"] = url
        article_data["article_category"] = "General" # Threads 沒分類
        
        # 互動數 (如果 LD-JSON 有 interactionStatistic 最好，沒有就給 0)
        interaction = ld_json.get("interactionStatistic", []) if ld_json else []
        like_count = 0
        comment_count = 0
        
        for item in interaction:
            itype = item.get("interactionType", "")
            if "LikeAction" in itype:
                like_count = item.get("userInteractionCount", 0)
            elif "CommentAction" in itype:
                comment_count = item.get("userInteractionCount", 0)
                
        article_data["reaction_count"] = like_count
        article_data["comment_count"] = comment_count
        
        article_data["content_keywords"] = []
        article_data["content_top_key"] = []
        article_data["comments"] = [] # 抓取 Threads 留言極難 (需 GraphQL)，先留空
        article_data["comments_top_key"] = []

        return article_data

    except Exception as e:
        print(f"程式執行錯誤: {e}")
        return None

# === 主程式 ===
if __name__ == "__main__":
    if "填入" in MY_COOKIE:
         print("❌ 請先填入 Cookie 才能執行！Threads 防護很嚴格。")
    else:
        result = parse_threads_post(target_url)
        
        if result:
            # 存檔
            safe_title = clean_filename(result["article_author"] + "_post")
            filename = f"Threads_{safe_title}.json"
            filepath = os.path.join(output_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            print(f"✅ 解析成功！已存檔至: {filepath}")
            print(f"內容摘要: {result['content_raw'][:50]}...")
        else:
            print("❌ 解析失敗。")