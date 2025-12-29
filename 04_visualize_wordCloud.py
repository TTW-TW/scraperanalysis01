import json
import re
import os # 處理路徑
import glob
import datetime
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ======= 手動調整參數區 =======

# 指定查詢的起迄時間 例如 "2025-12-01"
data_start_date_str = "2025-01-01" 
data_end_date_str = "2025-12-31"

# 輸入、輸出檔案路徑
input_folder = r"json_test/PTT/Jieba" 
output_folder = r"json_test/PTT/Jieba/Visualize/WordCloud" 
output_filename = f"wordcloud_result_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"

# 字型檔案放置區
font_path = r'font/Iansui-Regular.ttf'

# 遮罩圖案放置區
mask = np.array(Image.open(r"content/wordCloudMask/taiwan.jpg"))

# ======= 手動調整參數區 =======

now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d%H%M%S")
output_filename = f"heatmap_result_{timestamp_str}.png"
os.makedirs(output_folder, exist_ok=True)
output_file_path = os.path.join(output_folder, output_filename)



# 取得目標斷詞結果並轉為文字雲輸入格式
def get_all_cuts_result(df, start_dt, end_dt):

        cuts_list = []
        
        # --- 1. 文章處理 ---
        df_article = df.copy()
        # 轉換時間
        df_article['publish_time'] = pd.to_datetime(df_article['publish_time'])
        
        # 時間篩選
        mask_article = (df_article['publish_time'] >= start_dt) & (df_article['publish_time'] <= end_dt)
        target_articles = df_article[mask_article]
        
        # 取出 content_keywords (list)，並加入大池子
        # 使用 .dropna() 避免有些文章沒有關鍵字導致報錯
        for keywords in target_articles['content_keywords'].dropna():
                cuts_list.extend(keywords)
                
        print(f"文章處理完畢：納入 {len(target_articles)} 篇文章的關鍵字")

        # --- 2. 留言處理 ---
        df_temp = df.copy()
        
        # 炸開留言 (Explode)
        df_exploded = df_temp.explode('comments')
        # 移除空留言
        df_exploded = df_exploded.dropna(subset=['comments'])
        
        # 提取時間與關鍵字，裡要處理巢狀 dict，使用 apply 取值
        df_exploded['cmt_time'] = df_exploded['comments'].apply(lambda x: x.get('comment_date_format'))
        df_exploded['cmt_keywords'] = df_exploded['comments'].apply(lambda x: x.get('comment_keywords')) # 注意你的 JSON key 是單數
        
        # 轉換時間格式
        df_exploded['cmt_time'] = pd.to_datetime(df_exploded['cmt_time'])
        
        # 時間篩選
        mask_comment = (df_exploded['cmt_time'] >= start_dt) & (df_exploded['cmt_time'] <= end_dt)
        target_comments = df_exploded[mask_comment]
        
        # 取出 comment_keywords (它是 list)，並加入大池子
        for keywords in target_comments['cmt_keywords'].dropna():
                cuts_list.extend(keywords)
                
        print(f"留言處理完畢：納入 {len(target_comments)} 則留言的關鍵字")
        print(f"總共收集到 {len(cuts_list)} 個詞彙準備生成文字雲")
        
        return cuts_list

# 處理 input 時間格式
def format_filter_time(data_start_date_str, data_end_date_str):
    
    # 轉為時間格式
    start_dt = pd.to_datetime(data_start_date_str)
    
    # 加上時間，確保有包含到當天的 23:59:59
    end_dt = pd.to_datetime(data_end_date_str) + pd.Timedelta(hours=23, minutes=59, seconds=59)
    
    # 起訖日期誤繕防呆
    if start_dt > end_dt:
        print(f"⚠️ 警告：起始日 ({start_dt.date()}) 晚於結束日 ({end_dt.date()})，系統已自動調換順序。")
        start_dt, end_dt = end_dt, start_dt # Python 的變數交換語法
    
    return start_dt, end_dt

# 主程式
# 遍歷檔案所有檔案，將所有 json 放進超大陣列，並轉換為 dataframe
if __name__ == "__main__":   
        #  讀取所有 JSON 檔案
    json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本
    json_list = []

    for json_to_do in json_files:
        current_json_name = re.split(r'[/]+', json_to_do.replace( '\\', '/'))[-1]
        try:
            with open(json_to_do  , 'r', encoding='utf-8') as f:
                # json.load() 讀取檔案內容並解析成 Python 物件 (這裡會是個字典)
                article_json = json.load(f)
                # 把檔案名稱也存成dataframe 欄位
                article_json["source_filename"] = current_json_name
                json_list.append(article_json)
        except Exception as e:
            print(f"讀取錯誤 {current_json_name}: {e}")
        
        
        if not json_list:
            print("❌ 沒有讀取到任何資料，請檢查路徑。")
        else:
            df = pd.DataFrame(json_list) 
            
            # 格式化使用者輸入的時間
            start_dt, end_dt = format_filter_time(data_start_date_str, data_end_date_str)
            print(f"分析區間：{start_dt} 至 {end_dt}")

            # 取得目標斷詞結果並轉為文字雲輸入格式
            cuts_list = get_all_cuts_result(df, start_dt, end_dt)

    if len(cuts_list) > 0:
        # 轉換為文字雲需要的字串格式 (以空白分隔)
        text_for_cloud = " ".join(cuts_list)
    
        # 產製文字雲大陣列
        ## 文字雲基本參數
        ## width, height
        wordcloud = WordCloud(
            mask = mask , 
            margin = 1, scale = 2, 
            contour_color="#A4A7A5", 
            contour_width=3, 
            background_color = "black", 
            colormap = "Set3", 
            max_words = 80, min_font_size = 8, 
            font_path = font_path 
            ).generate(text_for_cloud)

        # 存檔
        wordcloud.to_file(output_file_path)
        print(f"文字雲已儲存至：{output_file_path}")
        
        # 繪圖
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
    else:
        print("該區間內沒有任何關鍵字資料，無法生成文字雲。")