import requests
from bs4 import BeautifulSoup


# request參數
domainName = 'https://www.ptt.cc/'

# 在此更新文章連結
target_url = 'https://www.ptt.cc/bbs/Gossiping/M.1766549895.A.9F9.html'


def parse_prr_article(target_url):
    
    # ==== 1. request 並繞過 18 歲標籤，基本連線檢查 ====
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': 'over18=1' # 讓伺服器知道已滿 18 歲
    }

    try:
        web = requests.get(target_url, headers=headers, timeout = 10)
        if web.status_code != 200:
            return None 
        soup = BeautifulSoup(web.text, "html.parser") # 使用 html.parser 解析器
        main_container = soup.find('div', id='main-content')
    except Exception as e:
        print(f"連線錯誤，訊息: {e}")
        return None

    # ==== 2. 爬取 metadata 作者標題 ====
    metadataList = {}
    # 使用尚未拔除的dom，邊爬邊拔除
    metadata = main_container.find_all('div', class_ = 'article-metaline')
    for m in metadata  :
        metaTag =  m.find('span', class_ = 'article-meta-tag').get_text(strip=True)
        metaValue =  m.find('span', class_ = 'article-meta-value').get_text(strip=True)
        metadataList[metaTag] =  metaValue
        m.extract()

    # 移除看板資訊
    metaDeletes2 = main_container.find_all('div', class_ ='article-metaline-right')

    for metaDelete2 in metaDeletes2:
        metaDelete2.extract() 

    # ==== 3.解析留言並同時移除 ====
    
    # 找出各別留言，提取 褒貶、作者、留言內容
    messageClean = []
    messageAll = main_container.find_all('div', class_ = 'push')
    for messageBranch in messageAll:
        msgTag = messageBranch.find('span', class_ ='push-tag' )
        msgAuthor = messageBranch.find('span', class_ ='push-userid' )
        msgContent = messageBranch.find('span', class_ ='push-content')
        
        # 確保都有存在才執行，避免出錯
        if msgTag and msgAuthor and msgContent:
            msgDictionary = {
                'msgTag' : msgTag.get_text(strip=True),
                'msgAuthor': msgAuthor.get_text(strip=True),
                'msgContent': msgContent.get_text(strip=True)
                }
            messageClean.append(msgDictionary)
        
        # 寫入後移除
        messageBranch.extract()
    
    print("留言數量 = " , len(messageClean), "則")
    # ==== 4. 移除其他雜訊  ====
    
    # 移除發信站: 批踢踢實業坊  
    messagesMetas = main_container.find_all('span', class_ ='f2')
    for messagesMeta  in messagesMetas:
        messagesMeta .extract() 
        
    # 移除留言中的圖片
    richcontents = main_container.find_all('div', class_ ='richcontent')
    for richcontent  in richcontents :
        richcontent .extract() 
        
    # ==== 5.取得乾淨內文  ====
    mainContent = main_container.get_text(strip=True)
    
    # ==== 6.回傳解析結果  ====
    return {
        'meta' : metadataList,
        'content' : mainContent,
        'comment' : messageClean
    }

print(parse_prr_article(target_url))

