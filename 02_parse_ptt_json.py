import requests
from bs4 import BeautifulSoup
import datetime
import json
import os
import time
import random
import re

# =================手動參數=================
# 填寫 準備分析的task_list 檔名
task_json_path = r"json_test/PTT/TaskList/task_list_20251229171952.json" 
log_folder = r"json_test/PTT/parse_log"


# 輸出位置(尚未斷詞的)
output_folder = r"json_test/PTT"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(log_folder, exist_ok=True)
current_time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
log_file_path = os.path.join(log_folder, f"scraper_log_{current_time_str}.txt")

timezone_tw = datetime.timezone(datetime.timedelta(hours=8))
# =============================================

# 清洗標題作為檔名用
def clean_filename(title):
    # 移除或替換檔名中的非法字元，免得產黨時出錯
    return re.sub(r'[\\/:*?"<>|]', '_', title)

# 解析 json 主程式
def parse_ptt_article(target_url):
    article_json = {} 
    article_json["article_source"] = 'PTT'
    article_json["article_url"] = target_url
    
    try:
        article_time_stamp = target_url.split("/")[-1].split(".")[1] # 直接拿網址串的時間戳為發布日期
        article_time = datetime.datetime.fromtimestamp(int(article_time_stamp) , tz=timezone_tw)
    except Exception as e:
        print(f"URL 解析時間失敗: {target_url}")
        return None 

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': 'over18=1'
    }
    
    ## 連線檢查
    try:
        web = requests.get(target_url, headers=headers, timeout = 20)
        if web.status_code != 200:
            return {'error': 'HTTP Error or Main Container Not Found'}
        soup = BeautifulSoup(web.text, "html.parser") # 使用 html.parser 解析器
        main_container = soup.find('div', id='main-content')
    except Exception as e:
        print(f"連線錯誤，訊息: {e}")
        return None

    # === 2. 取得屬性資訊，清整，並 extract ===
    
    metadataList = {}
    # 使用尚未拔除的dom，邊爬邊拔除
    # 看板
    metadata2 = main_container.find_all('div', class_ = 'article-metaline-right')
    for m in metadata2:
        metaTag =  m.find('span', class_ = 'article-meta-tag').get_text(strip=True)
        metaValue =  m.find('span', class_ = 'article-meta-value').get_text(strip=True)
        metadataList[metaTag] =  metaValue
        m.extract()   
    topbar_container = soup.find('div', id='topbar-container')
    first_board =   topbar_container.find('a', class_ = 'board').get_text(strip=True)
    board = first_board[2:]
        
    # 作者、標題、時間 
    metadata = main_container.find_all('div', class_ = 'article-metaline')
    for m in metadata  :
        metaTag =  m.find('span', class_ = 'article-meta-tag').get_text(strip=True)
        metaValue =  m.find('span', class_ = 'article-meta-value').get_text(strip=True)
        metadataList[metaTag] =  metaValue
        m.extract()
    
    # 寫入 JSON 所需欄位
    ## 有可能缺少標題欄位 (如 https://www.ptt.cc/bbs/Coffee/M.1764120927.A.20E.html)
    if len(metadataList) > 0:
        article_json["article_title"] = metadataList.get("標題", "無標題")
        article_json["article_category"] = board
        article_json["article_author"] = metadataList.get("作者", "unknown")
        article_json["publish_time"] = article_time.strftime("%Y-%m-%d %H:%M:%S")
        article_json["date_year"] = article_time.year
        article_json["date_month"] = article_time.month
        article_json["date_day"] = article_time.day
    else:
        article_json["article_title"] = "無標題"
        article_json["article_category"] = board
        article_json["article_author"] = ""
        article_json["publish_time"] = article_time.strftime("%Y-%m-%d %H:%M:%S")
        article_json["date_year"] = article_time.year
        article_json["date_month"] = article_time.month
        article_json["date_day"] = article_time.day
        print('⚠️' * 40)
        print(f"⚠️ 文章 {target_url} 缺少標題、作者欄位 ")
        print(f"⚠️ 請人工檢核並手動補上標題 ")
        print('⚠️' * 40)

    print("metadataList = " ,metadataList)
    
    
    # === 3. 取得留言，清整，並extract === 
    # 找出各別留言，提取 褒貶、作者、留言內容
    comments = []
    messageAll = main_container.find_all('div', class_ = 'push')
    for messageBranch in messageAll:
        msgTag = messageBranch.find('span', class_ ='push-tag' )
        msgAuthor = messageBranch.find('span', class_ ='push-userid' )
        msgContent = messageBranch.find('span', class_ ='push-content')
        msgTime_pre = messageBranch.find('span', class_ ='push-ipdatetime')
        
        
        # 確保都有存在才執行，避免出錯
        if msgTag and msgAuthor and msgContent and msgTime_pre:
            # 1. 取得文字並切割 (解決 IP 黏在一起或多個空白問題)
            raw_time_text = msgTime_pre.get_text(strip=True)
            msgTime_pre_list = raw_time_text.split()
            
            # 2. 永遠取「倒數兩個」元素 (日期 + 時間)
            # 這樣無論前面有沒有 IP (長度是 2 還是 3)，都能抓對
            if len(msgTime_pre_list) >= 2:
                clean_date = msgTime_pre_list[-2] # 日期 (如 12/29)
                clean_time = msgTime_pre_list[-1] # 時間 (如 18:30)
                
                # 3. 組合時間字串 (先假設是今年)
                time_str = f"{article_time.year}/{clean_date} {clean_time}"
                
                try:
                    msgTime = datetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M").replace(tzinfo=timezone_tw)
                    
                    # 4. 跨年邏輯 (若留言月份 < 文章月份，代表跨年了，年份+1)
                    if msgTime.month < article_time.month:
                        msgTime = msgTime.replace(year=article_time.year + 1)
                        
                except ValueError:
                    # 糟糕格式的預設值
                    msgTime = datetime.datetime(1970, 1, 1, tzinfo=timezone_tw)
            else:
                # 格式不完整 (只有日期沒時間等)
                msgTime = datetime.datetime(1970, 1, 1, tzinfo=timezone_tw)
            
            # 配合後面 Line 150 的 msgTime_pre_list 使用，把清洗後的結果存回去
            # 這樣 'comment_raw_time' 就會只顯示乾淨的 "日期 時間"
            msgTime_pre_list = [clean_date, clean_time] if len(msgTime_pre_list) >= 2 else ["Unknown"]


            msgContent = msgContent.get_text(strip=True)
            msgContent = msgContent[1:].strip()
            msgDictionary = {
                'comment_author': msgAuthor.get_text(strip=True),
                'comment_raw_time': " ".join(msgTime_pre_list),
                'comment_date_format': msgTime.strftime("%Y-%m-%d %H:%M:%S"),
                'comment_year': msgTime.year,
                'comment_month':msgTime.month,
                'comment_day':msgTime.day,
                'comment_tag' : msgTag.get_text(strip=True),                
                'comment_content': msgContent
                }
            comments.append(msgDictionary)
        
        # 寫入後移除
        messageBranch.extract()
    
    print("留言數量 = " , len(comments), "則")
    article_json["reaction_count"] = len(comments)
    article_json["comment_count"] = len(comments)
    
    # === 4. 清除不必要的雜訊 === 
    # 移除發信站: 批踢踢實業坊  
    messagesMetas = main_container.find_all('span', class_ ='f2')
    for messagesMeta  in messagesMetas:
        messagesMeta .extract() 
        
    # 移除留言中的圖片
    richcontents = main_container.find_all('div', class_ ='richcontent')
    for richcontent  in richcontents :
        richcontent .extract() 
    
      
    # === 5. 取得文章內文 === 
    mainContent = main_container.get_text(strip=True)
    
    article_json["content_raw"] = mainContent
    article_json["content_keywords"] = []
    article_json["content_top_key"] = []
    
    # === 6. 組合成初版 json 並返還=== 
    
    article_json["comments"] = comments
    article_json["comments_top_key"] = []
    
    return article_json

# 錯誤訊息 log
def write_log(msg):
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

if __name__ == "__main__":
    print(f"讀取任務: {task_json_path}")
    
    write_log(f"Task Source: {task_json_path}")
    write_log("-" * 50)
    
    try:
        with open(task_json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            
        print(f"總共 {len(tasks)} 篇任務")
        
        for i, task in enumerate(tasks):
            url = task['url']
            # 清洗標題作為檔名用
            safe_title = clean_filename(task['title'])
            
            print(f"[{i+1}/{len(tasks)}] {safe_title}")
            
            # 隨機延遲 5~10 秒
            sleep_time = random.uniform(5, 10)
            print(f"等待 {sleep_time:.1f} 秒", end="\r")
            time.sleep(sleep_time)
            
            result_json = parse_ptt_article(url)
            
            # 預設檔名 (萬一失敗時用)
            temp_filename = f"Unknown_{safe_title}.json"
            
            # 寫出檔案
            if result_json and 'error' not in result_json:
                category = result_json.get("article_category", "Unknown")
                # 再次清洗以防解析後的標題跟初始清單解析的不同
                final_title = clean_filename(result_json.get("article_title", safe_title))
                
                filename = f"{category}_{final_title}.json"
                
                
                # [Log 2] 檢查缺少標題或作者
                if result_json.get("article_author") == "unknown" or \
                   result_json.get("article_title") == "標題讀取失敗":
                    write_log(f"[Missing Meta] {filename}")
                
                # [Log 3] 檢查留言是否有 1970/01/01
                # 檢查邏輯：遍歷所有留言，看日期欄位是否以 "1970" 開頭
                has_invalid_date = False
                for comment in result_json.get("comments", []):
                    if comment.get("comment_date_format", "").startswith("1970"):
                        has_invalid_date = True
                        break
                if has_invalid_date:
                    write_log(f"[Invalid Date] {filename}")
                # 正常存檔
                filepath = os.path.join(output_folder, filename)    
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, ensure_ascii=False, indent=4)
                print(f"成功寫入檔案: {filename}")
            else:
                error_msg = result_json.get('error', 'Unknown Error') if result_json else "Return None"
                # [Log 1] 連線錯誤或解析失敗
                write_log(f"[Error] {temp_filename} | {error_msg}")
                print(f"寫入檔案失敗")
                
    except FileNotFoundError:
        print("找不到任務檔")
        write_log(f"找不到任務檔: {task_json_path}")