import requests, bs4

url = "https://www.dcard.tw/f"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
htmlfile = requests.get(url, headers = headers)
objsoup = bs4.BeautifulSoup(htmlfile.text, 'lxml')

articles = objsoup.find_all('article', class_ = 'tgn9uw-0 bReysV')

number = 0

for article in articles:
    title = article.find('a')
    emotion = article.find('div', class_ = 'cgoejl-3 jMiYgp')
    comment = article.find('div', class_ = 'uj732l-2 ghvDya')
    number += 1
    print("文章編號:", number)
    print("文章標題:", title.text)
    print("心情數量:", emotion.text)
    print("留言數量:", comment.text)
    print("="*100)
#請將C:\\spider\\修改為chromedriver.exe在您電腦中的路徑
from selenium import webdriver
import bs4
dirverPath = 'C:\\spider\\chromedriver.exe'
browser = webdriver.Chrome(executable_path = dirverPath)
url = 'https://www.dcard.tw/f'
browser.get(url)

objsoup = bs4.BeautifulSoup(browser.page_source, 'lxml')
articles = objsoup.find_all('article', class_ = 'tgn9uw-0 bReysV')

number = 0

for article in articles:
    title = article.find('a')
    emotion = article.find('div', class_ = 'cgoejl-3 jMiYgp')
    comment = article.find('div', class_ = 'uj732l-2 ghvDya')
    number += 1
    print("文章編號:", number)
    print("文章標題:", title.text)
    print("心情數量:", emotion.text)
    print("留言數量:", comment.text)
    print("="*100)
#請將C:\\spider\\修改為chromedriver.exe在您電腦中的路徑
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4, time

dirverPath = 'C:\\spider\\chromedriver.exe'
browser = webdriver.Chrome(executable_path = dirverPath)
url = 'https://www.dcard.tw/f'
browser.get(url)


move = browser.find_element_by_tag_name('body')
time.sleep(3)
move.send_keys(Keys.PAGE_DOWN) 
time.sleep(3)

objsoup = bs4.BeautifulSoup(browser.page_source, 'lxml')
articles = objsoup.find_all('article', class_ = 'tgn9uw-0 bReysV')

number = 0

for article in articles:
    title = article.find('a')
    emotion = article.find('div', class_ = 'cgoejl-3 jMiYgp')
    comment = article.find('div', class_ = 'uj732l-2 ghvDya')
    number += 1
    print("文章編號:", number)
    print("文章標題:", title.text)
    print("心情數量:", emotion.text)
    print("留言數量:", comment.text)
    print("="*100)
#請將C:\\spider\\修改為chromedriver.exe在您電腦中的路徑
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4, time

page = int(input("請輸入頁面向下捲動次數:"))
dirverPath = 'C:\\spider\\chromedriver.exe'
browser = webdriver.Chrome(executable_path = dirverPath)
url = 'https://www.dcard.tw/f'
browser.get(url)


number = 0
counter = 0
post_title = []

while page > counter:
    move = browser.find_element_by_tag_name('body')
    time.sleep(1)
    move.send_keys(Keys.PAGE_DOWN) 
    time.sleep(1)

    objsoup = bs4.BeautifulSoup(browser.page_source, 'lxml')
    articles = objsoup.find_all('article', class_ = 'tgn9uw-0 bReysV')



    for article in articles:
        title = article.find('a')
        emotion = article.find('div', class_ = 'cgoejl-3 jMiYgp')
        comment = article.find('div', class_ = 'uj732l-2 ghvDya')
        
        if title.text not in post_title:
            number += 1
            post_title.append(title.text)
            print("文章編號:", number)
            print("文章標題:", title.text)
            print("心情數量:", emotion.text)
            print("留言數量:", comment.text)
            print("="*100)
            
    counter += 1
    
print(post_title)