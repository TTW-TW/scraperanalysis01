import cloudscraper
import requests
from bs4 import BeautifulSoup
import json
import re


# === 包含 agent 檢查的 header === 
headers = {
    # request 時要寫，cloudscraper 會自動產生 User-Agent
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Referer': 'https://www.dcard.tw/',
    'Accept': 'application/json',
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    # "cookie":"""
    # _gcl_au=1.1.208113173.1766336319; _ga=GA1.1.892226519.1766336319; __cf_dm=YWRtaW46MDox.522.crc.cf4dca1e; dcsrd=7XOURuszzGoor8yJiTJql5_8; __cf_bm=eMW70zRXTFlD1XUywoxfo1HZBuIfrLhQOlmne4ohC7I-1766724687-1.0.1.1-vk2pIQVJtsQk99ao6kZH2x6Ud61IJLotMHuCYDdZL_gfDX3SzYtD9q2BDkFvvDVuYQGcM7mIPU8OhhuQQGknOcp_nsYde5BZmfsU3TMzc18; _cfuvid=EbPil.2qj0JFyFOd_qxJPvqsgPUl7MFKdS2pl08Fg3o-1766724687265-0.0.1.1-604800000; NID=53062639; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%222b216a0c-adef-4fba-a1e0-8136008ca471%5C%22%2C%5B1766336318%2C324000000%5D%5D%22%5D%5D%5D; FCNEC=%5B%5B%22AKsRol8G5gYQxPF95CVzXkt6XnT7Ozoy2mmlmFeOtJqzaFjkqsRSB2XkzPKPwHGzjfB7TD59A9CUqwJhUYtW5UL6J6vrCGi4u7k22lWpB1wLxU5KjxPZAYfW2xKgb-Y8hPTAYdZ2wMr7cUzri4av44ILCuJL6uNX8w%3D%3D%22%5D%5D; cf_clearance=uhr9VxydhBHCJvbb_Fe_KCdEX2nxaAhL8wqPGX_innM-1766724750-1.2.1.1-z2NrJ1O62iZ1aSEeXqv.nheHFbpDPH_t07tV_oxyYJ960b.iCDlfJGeP6dddAe0wc2X6CUYWdjTc6Lz.hFX3159wubu8MMDnFFqHPfL8bZep20qnZPmvPsUxvPcyFwkI9NlfJwDruMKAvMg9FFCYAquk3i7jmdJdIubklWEUPoFgvyX9kTdbytuuY6SQ_iv6zMF4_uaceRAh7o7zhxfLeEkD8KCAgPMhpH4BaTfOX1M; cf_chl_rc_ni=11; _ga_DSM1GSYX4C=GS2.1.s1766724680$o3$g1$t1766724807$j53$l0$h0
    # """
}

# ===  目標 api 設定 === 
# popular=false 是最新文章，true是熱門文章
# limit=30 (30~100)
target_board = 'talk' # 閒聊 talk, 感情 relationship
mainUrl = f'https://www.dcard.tw/service/api/v2/forums/{target_board}/posts?popular=false&limit=30' 


# === 發送請求 === 

# 建立 scraper 實體
scraper = cloudscraper.create_scraper()

try:
    
    web = scraper.get(mainUrl, headers=headers) 
    if web.status_code == 200: # 請求成功
        data = web.json()
        print(f"成功取得 {len(data)} 篇文章")
        if len(data) > 0:
            first_post = data[0]
            print(first_post)
    else:
        print(f"失敗，連項狀態碼 = {web.status_code}")
        print(f"錯誤訊攳 = {web.text}")
except Exception as e:
    print(f"連線發生錯誤: {e}")