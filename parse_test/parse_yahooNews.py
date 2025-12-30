from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import os
import datetime
import re

# ================= 參數設定 =================
target_url = 'https://tw.news.yahoo.com/%E5%85%B1%E8%BB%8D%E6%BC%94%E7%BF%92%E4%BE%B5%E5%8F%B0%E7%81%A312%E6%B5%AC%E9%A0%98%E6%B5%B7-%E5%9C%8B%E9%98%B2%E9%83%A8%E6%8E%88%E6%AC%8A%E4%BD%9C%E6%88%B0%E5%96%AE%E4%BD%8D%E9%81%A9%E6%99%82%E6%87%89%E5%B0%8D-022759022.html'
output_folder = r"json_test/Yahoo/Article"
os.makedirs(output_folder, exist_ok=True)

def get_yahoo_content_v13(url):
    print(f"啟動瀏覽器 (V13 JS 寄生版)...")
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    final_data = {}

    try:
        driver.get(url)
        
        # === 1. 確保內文載入 (修正 0 字問題) ===
        print("等待頁面載入...")
        try:
            # 等待內文區塊出現
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "caas-body")))
        except:
            print("⚠️ 內文等待逾時，可能載入較慢")

        time.sleep(2) # 多給一點緩衝時間讓文字渲染

        # 解析內文
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        h1 = soup.find('h1')
        title = h1.get_text(strip=True) if h1 else "Unknown Title"
        content_div = soup.find('div', class_='caas-body')
        content_raw = "\n".join([p.get_text(strip=True) for p in content_div.find_all('p')]) if content_div else ""
        publish_time = soup.find('time')['datetime'] if soup.find('time') else ""
        
        print(f"✅ 內文抓取: {len(content_raw)} 字")
        
        # === 2. 觸發留言區 (為了拿到 Crumb) ===
        print("滾動至底部觸發留言載入...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 定位留言 iframe
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, '/comments/')]"))
        )
        
        # 從 iframe src 解析 context ID
        src = iframe.get_attribute('src')
        match = re.search(r'context=([a-zA-Z0-9\-]+)', src)
        context_id = match.group(1) if match else None
        print(f"✅ Context ID: {context_id}")

        # 切換進 iframe 拿 Crumb
        driver.switch_to.frame(iframe)
        time.sleep(1)
        
        iframe_html = driver.page_source
        crumb_match = re.search(r'"crumb"\s*:\s*"([^"]+)"', iframe_html)
        crumb = crumb_match.group(1) if crumb_match else None
        
        # 有時候 crumb 會有跳脫字元，處理一下
        if crumb: 
            crumb = crumb.encode().decode('unicode_escape')
            print(f"✅ Crumb: {crumb}")
        
        # === 3. JS 寄生攻擊 (核心修改) ===
        # 我們不切回主頁面，直接在 iframe 裡面執行 fetch
        # 因為這個 iframe 的網域跟 API 是同源的 (或是它擁有正確的 cookie 權限)
        
        all_comments = []
        
        if context_id and crumb:
            print("🚀 開始執行瀏覽器內建 Fetch (JS)...")
            
            # 定義一個 JS 腳本，它會自動分頁抓取所有留言
            # 這段 JS 會在瀏覽器內部執行
            fetch_script = """
            var callback = arguments[arguments.length - 1];
            var contextId = arguments[0];
            var crumb = arguments[1];
            var allMessages = [];
            var offset = 0;
            var batchSize = 100;
            
            async function fetchAll() {
                while(true) {
                    // 建構 URL
                    var url = `https://tw.news.yahoo.com/_td-news/api/resource/canvass.getMessageListForContext_ns;context=${contextId};count=${batchSize};lang=zh-Hant-TW;sortBy=highestRated;index=v%3D1%3As%3DhighestRated%3Aoff%3D${offset}?crumb=${crumb}`;
                    
                    try {
                        var response = await fetch(url);
                        if (!response.ok) {
                            console.error("Fetch failed: " + response.status);
                            break;
                        }
                        var data = await response.json();
                        var messages = data.canvassMessages || [];
                        
                        if (messages.length === 0) break;
                        
                        // 簡化資料回傳，減少傳輸量
                        messages.forEach(msg => {
                            allMessages.push({
                                user: msg.details.userContext.nickname,
                                content: msg.details.userText,
                                time: msg.meta.createdAt,
                                likes: msg.reactionStats.count
                            });
                        });
                        
                        offset += messages.length;
                        // 簡單的防呆，避免無限迴圈，最多抓 1000 則
                        if (offset > 1000) break;
                        
                        // 稍微休息一下避免太快
                        await new Promise(r => setTimeout(r, 500));
                        
                    } catch (e) {
                        console.error(e);
                        break;
                    }
                }
                callback(allMessages);
            }
            
            fetchAll();
            """
            
            # 使用 execute_async_script 執行上面的 JS
            # 這是 Selenium 最強大的功能之一，可以等待 JS 跑完才回傳 Python
            try:
                # 設定腳本超時時間 (因為要抓很多頁，給它 60 秒)
                driver.set_script_timeout(60)
                js_result = driver.execute_async_script(fetch_script, context_id, crumb)
                
                print(f"✅ JS 回傳成功！共取得 {len(js_result)} 筆留言")
                
                # 轉換資料格式
                for item in js_result:
                    all_comments.append({
                        "user_name": item['user'],
                        "content": item['content'],
                        "time": datetime.datetime.fromtimestamp(item['time']).strftime('%Y-%m-%d %H:%M:%S'),
                        "likes": item['likes'],
                        "reply_count": 0
                    })
                    
            except Exception as e:
                print(f"❌ JS 執行失敗: {e}")

        # 整理最終資料
        final_data = {
            "article_title": title,
            "article_url": url,
            "publish_time": publish_time,
            "content_raw": content_raw,
            "comment_count": len(all_comments),
            "comments": all_comments
        }

    except Exception as e:
        print(f"主要流程錯誤: {e}")
    finally:
        driver.quit()
        
    return final_data

if __name__ == "__main__":
    data = get_yahoo_content_v13(target_url)
    
    if data:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"yahoo_news_v13_{timestamp}.json"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"\n檔案已儲存: {filepath}")
        print(f"內文長度: {len(data.get('content_raw', ''))}")
        print(f"留言數量: {data['comment_count']}")