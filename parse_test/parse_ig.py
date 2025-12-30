import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import re

# ================= 設定區 =================
# 目標 IG 連結
target_url = "https://www.instagram.com/p/CddCn9NrHx9/?img_index=1"
output_folder = r"json_test/Instagram"
os.makedirs(output_folder, exist_ok=True)

# 【請填入你的 Instagram Cookie】
# 務必包含 "sessionid", "csrftoken", "ds_user_id" 等關鍵欄位
MY_COOKIE = 'ig_did=F69C1B81-CD3D-4CBE-B199-2B01B2482930; mid=aGEySAALAAGIcwwqfEntmgnNZrEz; datr=0_GraFJjc4cJfUBpsRiDn1N7; ps_l=1; ps_n=1; csrftoken=kAYEBFcq3BIWVkO1LYUYJou5U75tdNO1; ds_user_id=1400624058; dpr=1.53125; sessionid=1400624058%3A59hjzbPQ3jWoAh%3A17%3AAYjfK7GLgnV1KxUATZA-xtS7AN4igl_129OBXWU16w; wd=1254x150; rur="PRN\0541400624058\0541798560179:01fef008525bbfff081b6fd5ca1dc3762f6915e115f7c9bfd13d1ffeb78dcd7d9853cd71"' 
# ==========================================

def clean_filename(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)

def parse_instagram_post(url):
    # 1. 清洗網址 (移除 ?img_index=1 這種參數，只留文章 ID)
    # 範例: https://www.instagram.com/p/CddCn9NrHx9/
    base_url = url.split("?")[0]
    if not base_url.endswith("/"):
        base_url += "/"
        
    print(f"目標網址: {base_url}")

    # 2. 偽裝 Headers (IG 對 User-Agent 檢查很嚴)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "Cookie": MY_COOKIE,
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        print("正在連線至 Instagram...")
        resp = requests.get(base_url, headers=headers)
        
        # 3. 檢查是否被導向登入頁 (IG 沒登入通常會回傳 200 但內容是 Login page)
        if "Login • Instagram" in resp.text or "登入 • Instagram" in resp.text:
            print("❌ 失敗：被導向登入頁面，請更新 Cookie！")
            return None
            
        if resp.status_code != 200:
            print(f"❌ 抓取失敗: {resp.status_code}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        
        # === 解析邏輯 (依賴 Open Graph 標籤) ===
        article_data = {}
        
        # 標題 (通常是 "帳號 on Instagram: '內文前幾字'")
        og_title = soup.find("meta", property="og:title")
        raw_title = og_title["content"] if og_title else "Instagram Post"
        
        # 內文 (IG 把內文放在 og:description 裡面)
        og_desc = soup.find("meta", property="og:description")
        raw_content = og_desc["content"] if og_desc else ""
        
        # 嘗試分離 作者 與 內文
        # 格式通常是: "1,234 likes, 56 comments - username on May 12, 2022: \"這裡才是內文...\""
        if ": \"" in raw_content:
            parts = raw_content.split(": \"", 1)
            # 前半段可能包含讚數和作者，後半段是內文
            content_text = parts[1].rstrip('"') # 去掉最後的引號
            
            # 嘗試抓作者 (從 title 抓比較準: "Username on Instagram")
            if " on Instagram" in raw_title:
                author = raw_title.split(" on Instagram")[0]
            else:
                author = "Unknown"
        else:
            # 格式不符，直接全部當內文
            content_text = raw_content
            author = "Unknown"

        # 填入資料
        article_data["article_title"] = f"IG Post by {author}"
        article_data["article_author"] = author
        article_data["content_raw"] = content_text
        
        # 時間處理 (IG HTML 很難抓準確時間，除非解析 JSON，這裡用當下時間當備案)
        # 嘗試找看看有沒有 ld+json
        try:
            # 有時候會有 JSON
            # 但 IG 的 JSON 結構變動極快，這裡不強求，找不到就用現在時間
            now = datetime.datetime.now()
            article_data["publish_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            article_data["date_year"] = now.year
            article_data["date_month"] = now.month
            article_data["date_day"] = now.day
        except:
             pass

        # === 補齊 PTT 結構欄位 ===
        article_data["article_source"] = "Instagram"
        article_data["article_url"] = base_url
        article_data["article_category"] = "Post"
        
        article_data["reaction_count"] = 0 # 需進階解析 JSON 才有
        article_data["comment_count"] = 0  # 需進階解析 JSON 才有
        
        article_data["content_keywords"] = []
        article_data["content_top_key"] = []
        article_data["comments"] = [] # IG 留言也是 GraphQL，這裡留空
        article_data["comments_top_key"] = []

        return article_data

    except Exception as e:
        print(f"程式執行錯誤: {e}")
        return None

# === 主程式 ===
if __name__ == "__main__":
    if "貼上" in MY_COOKIE:
        print("❌ 請先填入 Instagram Cookie！(這一步不能省)")
    else:
        result = parse_instagram_post(target_url)
        
        if result:
            safe_title = clean_filename(result["article_author"] + "_IG_Post")
            filename = f"IG_{safe_title}.json"
            filepath = os.path.join(output_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            print(f"✅ 解析成功！已存檔至: {filepath}")
            print(f"抓到的內文片段: {result['content_raw'][:50]}...")
        else:
            print("❌ 解析失敗。")