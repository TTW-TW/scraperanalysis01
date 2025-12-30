import requests
from bs4 import BeautifulSoup
import json
import datetime
import os

# ================= 參數設定 =================
target_url = 'https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRFZxYUdjU0JYcG9MVlJYR2dKVVZ5Z0FQAQ?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
output_folder = r"json_test/GoogleNews/TaskList"
os.makedirs(output_folder, exist_ok=True)

headers = {
    # 這裡的 User-Agent 模擬一般瀏覽器，Google 通常會回傳含有 JS 的複雜版本
    # 但關鍵內容 (標題/連結) 依然存在於 HTML 中
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

base_url = 'https://news.google.com'

def find_parent_with_time(element):
    """往上層尋找包含 <time> 的父元素"""
    parent = element.parent
    # 往上找 5 層，避免無窮迴圈
    for _ in range(5):
        if parent is None: break
        time_tag = parent.find('time')
        if time_tag:
            return time_tag
        parent = parent.parent
    return None

def find_source_nearby(element, title_text):
    """嘗試在標題附近尋找新聞來源"""
    # 邏輯：往上找一層容器，然後找裡面的其他文字
    parent = element.parent
    for _ in range(3): # 往上找 3 層
        if parent is None: break
        
        # 來源通常是一個連結或 div，且文字不等於標題
        # 這裡簡單抓取：該區塊內所有文字，排除標題本身
        candidates = parent.find_all(['a', 'div'])
        for c in candidates:
            txt = c.get_text(strip=True)
            # 簡單過濾：長度短(通常來源名稱不長)、且不是標題、且不包含 '...'
            if 0 < len(txt) < 20 and txt != title_text and 'articles' not in c.get('href', ''):
                return txt
        parent = parent.parent
    return "Unknown"

if __name__ == "__main__":
    print(f"開始爬取 Google News (V2 修復版)...")
    
    news_list = []
    seen_urls = set() # 用來過濾重複的連結
    
    try:
        web = requests.get(target_url, headers=headers)
        
        if web.status_code == 200:
            soup = BeautifulSoup(web.text, "html.parser")
            
            # === 核心修改：不找 article，改找特定連結 ===
            # 找出所有 href 屬性以 ./articles/ 開頭的 a 標籤
            # 並且該標籤必須包含文字 (過濾掉只有圖片的連結)
            links = soup.select('a[href^="./articles/"]')
            
            print(f"初步找到 {len(links)} 個連結，開始解析...")
            
            for link in links:
                title = link.get_text(strip=True)
                
                # 過濾規則：
                # 1. 標題不能為空
                # 2. 避免重複抓取 (Google 有時會有圖片連結和文字連結指向同一篇)
                href = link['href'].replace('./', '/')
                full_url = base_url + href
                
                if not title or full_url in seen_urls:
                    continue
                
                seen_urls.add(full_url)

                # 嘗試找時間 (透過往上層搜尋)
                time_tag = find_parent_with_time(link)
                publish_time = time_tag['datetime'] if time_tag else "Unknown"
                
                # 嘗試找來源
                source_name = find_source_nearby(link, title)

                data = {
                    'title': title,
                    'source': source_name,
                    'url': full_url,
                    'publish_time': publish_time,
                    'scraped_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # 簡單顯示進度
                print(f"[{len(news_list)+1}] {data['source']} - {data['title'][:30]}...")
                news_list.append(data)
                
        else:
            print(f"連線失敗: {web.status_code}")

    except Exception as e:
        print(f"發生錯誤: {e}")

    # === 輸出 JSON ===
    if news_list:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        json_filename = f"google_news_list_v2_{timestamp}.json"
        json_filepath = os.path.join(output_folder, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=4)
            
        print(f"\n成功抓取 {len(news_list)} 篇新聞！")
        print(f"檔案已儲存: {json_filepath}")
        
        # 寫入簡易 Log
        log_filepath = os.path.join(output_folder, f"log_v2_{timestamp}.txt")
        with open(log_filepath, 'w', encoding='utf-8') as f:
            f.write(f"抓取時間: {datetime.datetime.now()}\n")
            f.write(f"抓取數量: {len(news_list)}\n")
    else:
        print("\n依然沒有抓到新聞，可能需要檢查 HTML 結構是否再次變更。")