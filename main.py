import requests
from bs4 import BeautifulSoup


# 批踢踢 domain name
domainName = 'https://www.ptt.cc/'

mainUrl = 'https://www.ptt.cc/bbs/Military/index.html' 
web = requests.get(mainUrl) 
soup = BeautifulSoup(web.text, "html.parser") # 使用 html.parser 解析氣(也可替換為 html5lib)
title = soup.title  

# 印出軍事版的 title 和文章網頁
print("=" * 80)
print("軍事版的 title 和文章網頁")
print("=" * 80)

# 主結構
article = soup.select('div.r-ent')
for a in article:
    title = a.find('a').get_text()
    date = a.find('div', class_ = 'date').get_text()
    articleUrl = a.find('a')['href']
    print('日期 = ', date, ', 標題：', title)
    print(domainName + articleUrl )
    



    
