import requests
from bs4 import BeautifulSoup
import re

# request 帶有 18 歲標籤
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Cookie': 'over18=1' # 加上這行讓伺服器知道已滿 18 歲
}

# 批踢踢 domain name
domainName = 'https://www.ptt.cc/'
mainUrl = 'https://www.ptt.cc/bbs/Gossiping/index.html' 


web = requests.get(mainUrl, headers=headers) 
soup = BeautifulSoup(web.text, "html.parser") # 使用 html.parser 解析氣(也可替換為 html5lib)
title = soup.title  

# 印出八卦版的 title 和文章網頁
print("=" * 80)


# 某一頁的主結構
article = soup.select('div.r-ent')
for a in article:
    if a.find('a') is None:  # 有些文章被刪除，沒有 a 標籤
        continue
    else:
        title = a.find('a').get_text()
        date = a.find('div', class_ = 'date').get_text()
        articleUrl = a.find('a')['href']
        print('日期 = ', date, ', 標題：', title)
        print(domainName + articleUrl )
    
    

print("=" * 80)

previousPage = soup.find('a', string = re.compile(r'上頁', re.IGNORECASE )) # 找到 tag 內匹配的文字，忽略大小寫
print('上一頁的網址 = ')
print(domainName + previousPage['href'])
    
