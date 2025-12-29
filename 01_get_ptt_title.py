import requests
from bs4 import BeautifulSoup
import json
import time
import random
import datetime
import os

# ================= 手動調整參數 =================
# 1. 目標看板網址 (填入該板的首頁，例如 Coffee, Gossiping, Stock)
target_board_url = 'https://www.ptt.cc/bbs/C_Chat/index.html'

# 2. 停止條件 (看誰先達到)

# 最早追溯日期 (YYYY-MM-DD)
stop_date_str = "2024-01-01" 
# 最大抓取篇數
max_article_count = 200

# 3. 輸出設定
output_folder = r"json_test/PTT/TaskList"
os.makedirs(output_folder, exist_ok=True) # 沒路徑就自動產生

## request 帶有 18 歲標籤
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Cookie': 'over18=1'
}

domainName = 'https://www.ptt.cc'

# 取得「上一頁」的網址
def get_previous_page_url(soup):
    try:
        # 找到包含 "上頁" 文字的連結
        paging_div = soup.find('div', class_='btn-group btn-group-paging')
        link = paging_div.find_all('a')[1] # 第二個按鈕是上一頁
        if '上頁' in link.get_text():
            return domainName + link['href']
    except:
        return None
    return None

# 時間格式標準化+年份推測 '12/25' 轉為 datetime 物件 
def parse_date(date_str, current_year):
    try:
        # date_str 格式通常為 "12/25" 或 " 5/01" 要處理調空白
        date_str = date_str.strip()
        month, day = map(int, date_str.split('/'))
        return datetime.datetime(current_year, month, day)
    except:
        return None

# 處理置頂區文章
def parse_article_block(ent_div, current_year):
    if ent_div.find('a') is None:
        return None
    
    title = ent_div.find('a').get_text()
    article_url = domainName + ent_div.find('a')['href']
    date_str = ent_div.find('div', class_='date').get_text()
    
    article_date = parse_date(date_str, current_year)
    
    return {
        'title': title,
        'url': article_url,
        'date': date_str,
        'parsed_date': article_date
    } # 回傳字典型態

if __name__ == "__main__":
    current_url = target_board_url
    
    task_list = [] # 一般文章
    sticky_list = []    # 置頂文章暫存區 (避免隨意觸發停止邏輯)
    
    # 初始化年份 (預設為今年，稍後在迴圈中動態調整)
    current_year = datetime.datetime.now().year
    stop_date = datetime.datetime.strptime(stop_date_str, "%Y-%m-%d")
    
    # 記錄最後狀態準備寫 log
    last_page_url = ""
    last_article_url = ""
    last_article_title = ""
    
    print(f"開始爬取任務... 目標: {stop_date_str}或 {max_article_count} 篇")

    while True:
        print(f"正在爬取頁面: {current_url}")
        
        try:
            # 加入隨機延遲 5~10 秒
            sleep_time = random.uniform(5, 10)
            print(f"正在休息 {sleep_time:.2f} 秒...", end="\r")
            time.sleep(sleep_time)

            web = requests.get(current_url, headers=headers)
            if web.status_code != 200:
                print(f"連線失敗: {web.status_code}")
                break
                
            soup = BeautifulSoup(web.text, "html.parser")
            
            # !! 分離置頂文章與一般文章 
            sep_div = soup.find('div', class_='r-list-sep') # 批踢踢裡的分隔線
            
            if sep_div:
                # 若有分隔線：
                # 1. 取得分隔線之後的兄弟元素 (置頂文)
                sticky_divs = sep_div.find_next_siblings('div', class_='r-ent')
                
                # 2. 取得分隔線之前的兄弟元素 (一般文)
                normal_divs = sep_div.find_previous_siblings('div', class_='r-ent')
                
                # 處理置頂文 (只解析，不檢查停止條件，只抓一次)
                # 為了避免每次翻頁都重複抓(假如置頂區有一直出現)
                if len(sticky_list) == 0: 
                    for div in sticky_divs:
                        data = parse_article_block(div, current_year)
                        if data:
                            print(f"  [置頂] {data['title']}")
                            sticky_list.append(data)
            else:
                # 若無分隔線，整頁都是一般文章
                # soup.select 預設抓出來是舊到新， 要 reversed 變成由心道就
                normal_divs = list(reversed(soup.select('div.r-ent')))

            # === 處理一般文章 (Normal Posts) ===
            for div in normal_divs:
                data = parse_article_block(div, current_year)
                if not data: continue

                article_date = data['parsed_date']
                
                # 跨年邏輯 (12、11、10...到1就要減一年)
                if task_list and article_date:
                    if article_date > datetime.datetime.now():
                         article_date = article_date.replace(year = current_year - 1)
                         data['parsed_date'] = article_date

                # 1. 日期停止檢查
                if article_date and article_date < stop_date:
                    print(f"達到日期停止條件: {data['date']} < {stop_date_str}")
                    current_url = None
                    break
                
                task_list.append(data)
                last_article_title = data['title']
                last_article_url = data['url']
                
                # 2. 數量停止檢查
                if len(task_list) >= max_article_count:
                    print(f"達到數量停止條件: {len(task_list)} >= {max_article_count}")
                    current_url = None 
                    break
            
            if current_url is None:
                break
                
            last_page_url = current_url
            current_url = get_previous_page_url(soup)
            if current_url is None:
                break
                
        except Exception as e:
            print(f"發生錯誤: {e}")
            break

    # === 合併置頂文章 ===
    # 將置頂文章加到一班文章最後面 
    print(f"加入 {len(sticky_list)} 篇置頂文章...")
    task_list.extend(sticky_list)

    # === 輸出 ===
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 移除 parsed_date (無法序列化)
    for task in task_list:
        if 'parsed_date' in task: del task['parsed_date']
        
    task_filename = f"task_list_{timestamp}.json"
    task_filepath = os.path.join(output_folder, task_filename)
    
    with open(task_filepath, 'w', encoding='utf-8') as f:
        json.dump(task_list, f, ensure_ascii=False, indent=4)
        
    print(f"任務清單已輸出: {task_filepath}")

    log_filename = f"scraper_log_{timestamp}.txt"
    with open(os.path.join(output_folder, log_filename), 'w', encoding='utf-8') as f:
        f.write(f"執行時間: {datetime.datetime.now()}\n")
        f.write(f"一般文章數: {len(task_list) - len(sticky_list)}\n")
        f.write(f"置頂文章數: {len(sticky_list)}\n")
        f.write(f"最後一般文章: {last_article_title}\n")
        f.write(f"最後一般文章網址: {last_article_url}\n")
        f.write(f"最後停留頁面: {last_page_url}\n")