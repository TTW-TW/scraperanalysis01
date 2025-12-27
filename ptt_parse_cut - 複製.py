import requests
from bs4 import BeautifulSoup
import datetime



article_json = {}
assume_date = datetime.datetime.now() # ⚠️抓不到文章標題時的假定日期，需人工檢核⚠️

target_url = 'https://www.ptt.cc/bbs/Coffee/M.1764120927.A.20E.html'
article_time_stamp = target_url.split("/")[-1].split(".")[1]
print(article_time_stamp )

# 批踢踢日期轉換
def format_ptt_time(origin_time):
    
    origin_time_switch = origin_time.split(" ")
    # 標準格式 Thu Dec 25 11:48:32 2025； 預防格式Mon Dec  8 22:59:33 2025
    for i in range(len(origin_time_switch) - 1):
        if len(origin_time_switch[i].replace(" ", "")) == 0: # 避免有多餘空格
            del origin_time_switch[i]
    month = origin_time_switch[1]
    day = origin_time_switch[2]
    times = origin_time_switch[3]
    year = origin_time_switch[4]

    x = day + " " + month + " " + year + " " + times 
    formatted_time = datetime.datetime.strptime( x, "%d %b %Y %H:%M:%S")
    month_formatted = formatted_time.month
    return formatted_time , day, month_formatted , year


# 解析 ptt 並存為目標 json 格式

def parse_ptt_article(target_url):
    article_json["article_source"] = 'PTT'
    article_json["article_url"] = target_url
    
    # === 1. 用瀏覽器執行請求 === 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': 'over18=1' # 讓伺服器知道已滿 18 歲
    }
    
    ## 連線檢查
    try:
        web = requests.get(target_url, headers=headers, timeout = 20)
        if web.status_code != 200:
            return None
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
        article_json["article_title"] = metadataList["標題"]
        article_json["article_category"] = metadataList["看板"]
        article_json["article_author"] = metadataList["作者"]
        a_formatted_time , a_day , a_month , a_year = format_ptt_time(metadataList["時間"])
        article_json["publish_time"] = a_formatted_time.strftime("%Y-%m-%d %H:%M:%S")
        article_json["date_year"] = a_year
        article_json["date_month"] = a_month
        article_json["date_day"] = a_day
    else:
        article_json["article_title"] = ""
        article_json["article_category"] = board
        article_json["article_author"] = ""
        article_json["publish_time"] = assume_date.strftime("%Y-%m-%d %H:%M:%S")
        article_json["date_year"] = assume_date.year
        article_json["date_month"] = assume_date.month
        article_json["date_day"] = assume_date.day
        print('⚠️' * 40)
        print(f"⚠️ 文章 {target_url} 缺少標題、作者、日期欄位 ")
        print(f"⚠️ 請人工檢核 assume_date 參數日期，並手動補上標題 ")
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
            msgTime_pre_list = msgTime_pre.get_text(strip=True).split(" ")
            
            if len(msgTime_pre_list) > 2: # 有 ip 版本 (會有 ip、日期、時間)
                msgTime_pre_list = msgTime_pre_list[1:] # 移除 ip 資訊保留日期
                origin_msgTime = " ".join(msgTime_pre_list)
                
                if len(metadataList) > 0: # 如果有標題作者欄位，可與推文時間比較
                    msgTime = str(a_year) + "/" + origin_msgTime # 跨年度邏輯驗證
                    if a_formatted_time > datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M"):
                        msgTime = str(int(a_year) + 1) + "/" + origin_msgTime
                        msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")
                    else:
                        msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")
                else: # 如果沒有標題作者欄位，則不與推文時間比較
                    msgTime = str(assume_date.year) + "/" + origin_msgTime
                    msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")
            else: # 無 ip 版本
                origin_msgTime = " ".join(msgTime_pre_list)
                
                if len(metadataList) > 0: # 如果有標題作者欄位，可與推文時間比較
                    msgTime = str(a_year) + "/" + origin_msgTime
                    if a_formatted_time > datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M"):
                        msgTime = str(int(a_year) + 1) + "/" + origin_msgTime
                        msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")
                    else:
                        msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")
                else:  # 如果沒有標題作者欄位，則不與推文時間比較
                    msgTime = str(assume_date.year) + "/" + origin_msgTime
                    msgTime = datetime.datetime.strptime(msgTime, "%Y/%m/%d %H:%M")

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
    
    # === 6. 組合成初版 json 並返還=== 
    
    article_json["comments"] = comments
    
    return article_json
    

print("=" * 80)
print(parse_ptt_article(target_url))