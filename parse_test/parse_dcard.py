import cloudscraper
import json
import datetime
import time
import os
import re

# ================= 設定區 =================
# 目標 Dcard 文章網址
target_url = "https://www.dcard.tw/f/talk/p/260563315"
output_folder = r"json_test/Dcard"
os.makedirs(output_folder, exist_ok=True)

# 【請填入你剛剛複製的 Cookie】
# 記得要用引號包起來，變成字串
MY_COOKIE = '_gcl_au=1.1.208113173.1766336319; _ga=GA1.1.892226519.1766336319; __cf_bm=NQKZs82zaxknnggIF4XiH9.WD.NCjLL4VQILqhGgnWY-1767022590-1.0.1.1-434b4xV2xY7wMFdM0tbx7R4icAN2hreNVx3taHRStdb2w2o9alAG.pyPxQkyx2ixgDnGKeeizHt265aUuKvW6.BIm931QtJQKTIOnsyG11s; _cfuvid=L3Dzdxg5PeEZA1dSKg7gm9UvWJ5uM0FueFisVHKhPSA-1767022590100-0.0.1.1-604800000; NID=53062639; dcsrd=hXh4fmBHqGFPrwk-2BCmatfv; cf_clearance=qIyuAcXmUzFQ.sUOI085.LUlZi1WPZVbKrJ7HMRHH50-1767022590-1.2.1.1-sBFnSaH8wCMzV749Zps1CArgZlzNKQzyTWtWivHExASqHbSZGroks4KFEbCf.2nQT40Wbo1O7Mk8lPBcd_3xHeLoMixznipwy7PusdjWzNrIMAPYgkrKbl0LWJxJghHieDgUyxF2DqmzzQvJqU9GUlvnaL9jXT3dVibJXR0RfQsXSCOTAmGq.N.3RGg8oAtFHsykR640hj_LMRcIro6HASQA225rCVHePIMYeb5jWHo; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%222b216a0c-adef-4fba-a1e0-8136008ca471%5C%22%2C%5B1766336318%2C324000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol8wEayhayv6Bp1jco-hCUuW-LXpOS7BBxv-OoD_khpTk8KqaOyH_cvybp9eI3r0EfqS_n8kCxf6RdCq2MXE2lyRbg2_W8z1TvntHV71h6ZDxTfHYTzighMKcY6yGtWZjNNkOLrwnQQLDxfY5T7RtraeSzjsZQ%3D%3D%22%5D%5D; __cf_dm=YWRtaW46MDox.484.crc.cf4dca1e; _ga_DSM1GSYX4C=GS2.1.s1767022589$o5$g1$t1767023034$j60$l0$h0'
# ==========================================

def parse_dcard_time(iso_time_str):
    """
    將 Dcard 的 ISO 8601 時間格式 (ex: 2024-12-29T10:00:00.000Z)
    轉為我們需要的 datetime 物件 (轉為台灣時間 +8)
    """
    try:
        # 解析 ISO 格式 (UTC)
        dt_utc = datetime.datetime.strptime(iso_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        # 加 8 小時轉台灣時間
        dt_tw = dt_utc + datetime.timedelta(hours=8)
        return dt_tw
    except Exception as e:
        print(f"時間解析失敗: {e}")
        return datetime.datetime.now()

def get_dcard_json(url):
    # 初始化 scraper
    scraper = cloudscraper.create_scraper()
    
    # 【重點修正】：偽裝成真實瀏覽器的 Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.dcard.tw/",
        "Cookie": MY_COOKIE  # 帶上通行證
    }
    
    try:
        post_id = url.split("/p/")[-1].split("?")[0]
    except:
        print("網址格式錯誤")
        return None

    print(f"正在抓取 Dcard 文章 ID: {post_id}")

    api_post_url = f"https://www.dcard.tw/service/api/v2/posts/{post_id}"
    
    try:
        # 【重點修正】：請求時帶上 headers
        resp = scraper.get(api_post_url, headers=headers)
        
        if resp.status_code != 200:
            print(f"文章抓取失敗: {resp.status_code}")
            # 如果失敗，印出內容看一下是不是被擋
            # print(resp.text) 
            return None
        
        post_data = resp.json()
        print("文章本體抓取成功！") # Debug 訊息
        
    except Exception as e:
        print(f"連線錯誤: {e}")
        return None

    # === 步驟 B: 抓取留言 (API) ===
    # 這裡也要帶 headers
    api_comment_url = f"https://www.dcard.tw/service/api/v2/posts/{post_id}/comments?limit=100"
    comments_data = []
    
    try:
        # 【重點修正】：請求時帶上 headers
        resp_c = scraper.get(api_comment_url, headers=headers)
        if resp_c.status_code == 200:
            comments_data = resp_c.json()
            print(f"抓到 {len(comments_data)} 則留言")
    except Exception as e:
        print(f"留言抓取失敗: {e}")

    # === 步驟 C: 整理成你的 JSON 格式 ===
    article_json = {}
    
    # 時間處理
    pub_dt = parse_dcard_time(post_data.get("createdAt"))
    
    article_json["article_source"] = "Dcard"
    article_json["article_url"] = url
    article_json["article_title"] = post_data.get("title", "無標題")
    article_json["article_category"] = post_data.get("forumAlias", "Unknown") # 看板
    article_json["article_author"] = post_data.get("school", "匿名") # Dcard 作者通常顯示學校
    
    article_json["publish_time"] = pub_dt.strftime("%Y-%m-%d %H:%M:%S")
    article_json["date_year"] = pub_dt.year
    article_json["date_month"] = pub_dt.month
    article_json["date_day"] = pub_dt.day
    
    article_json["reaction_count"] = post_data.get("reactionCount", 0)
    article_json["comment_count"] = post_data.get("commentCount", 0)
    
    # 整理內文 (Dcard 內文直接是純文字，只要處理換行)
    article_json["content_raw"] = post_data.get("content", "")
    article_json["content_keywords"] = []
    article_json["content_top_key"] = []

    # 整理留言
    formatted_comments = []
    for c in comments_data:
        if c.get("hidden", False): # 跳過被隱藏/刪除的留言
            continue
            
        cmt_dt = parse_dcard_time(c.get("createdAt"))
        
        cmt_dict = {
            "comment_author": c.get("school", "匿名"),
            "comment_raw_time": c.get("createdAt"), # 保留原始格式備查
            "comment_date_format": cmt_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "comment_year": cmt_dt.year,
            "comment_month": cmt_dt.month,
            "comment_day": cmt_dt.day,
            "comment_tag": f"B{c.get('floor', 0)}", # Dcard 的樓層 (B1, B2)
            "comment_content": c.get("content", "")
        }
        formatted_comments.append(cmt_dict)

    article_json["comments"] = formatted_comments
    article_json["comments_top_key"] = []

    return article_json

# === 主程式 ===
if __name__ == "__main__":
    print(f"開始抓取: {target_url}")
    
    data = get_dcard_json(target_url)
    
    if data:
        # 檔名清洗
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', data["article_title"])
        filename = f"Dcard_{safe_title}.json"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"成功存檔: {filepath}")
        print(f"共取得 {len(data['comments'])} 則留言")
    else:
        print("抓取失敗")