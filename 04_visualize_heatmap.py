import json
import re
import os # 處理路徑
import glob
import pandas as pd
import numpy as np
from PIL import Image
from matplotlib.font_manager import FontProperties # 指定字體
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# 指定出圖的文字為微軟正黑體(適用於專案內沒有放字型)
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 指定字體
# plt.rcParams['axes.unicode_minus'] = False # 解決負號無法顯示的問題

# 指定出圖的文字為香菜體 (僅適用於專案資料夾有放字型)
font_path = r"font/Iansui-Regular.ttf"
my_font = FontProperties(fname=font_path)


# ======= 手動調整參數區 =======
# 設定要分析的關鍵字
target_keywords = ["自己", "現在", "台灣", "中國", "遊戲"]

# 指定查詢的起迄時間 例如 "2025-12-01"
data_start_date_str = "2025-01-01" 
data_end_date_str = "2025-12-31"

# 輸入、輸出檔案路徑
input_folder = r"json_test/PTT/Jieba" 
output_folder = r"json_test/PTT/Jieba/Visualize/Heatmap" 

# ======= 手動調整參數區 =======

now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d%H%M%S")
output_filename = f"heatmap_result_{timestamp_str}.png"
os.makedirs(output_folder, exist_ok=True)
output_file_path = os.path.join(output_folder, output_filename)


json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本
json_list = []
# df = pd.DataFrame(json_list)

# 練習：產製二維樞紐分析
def cal_pivot_table(df):
    
    # 時間格式化
    df['publish_time'] = pd.to_datetime(df["publish_time"])
    df['date']  = df['publish_time'].dt.date
    df['day']  = df['publish_time'].dt.day
    df['hour'] = df['publish_time'].dt.hour
    # print(df['hour'])
    
    # values關鍵字參數就是所要計算的欄位，預設為該欄位資料的平均值
    # index關鍵字參數則是群組(groupby)的欄位
    pivot_data = df.pivot_table(values = 'comment_count', 
                                  index = 'day' , 
                                  aggfunc = np.sum 
                                  # 統計方式，也可以傳入多個或自訂函數 aggfunc=[np.mean, np.sum, len]
                                  # sum、mean、median、max、min、std、len、
                                  )
    
    # 樞紐分析
    print(pivot_data )
    
    return pivot_data 

# 練習：產製熱力圖資料 (三維分析)，不含無資料時間
def create_heatmap_data(df):
    
    # 時間格式化
    df['publish_time'] = pd.to_datetime(df["publish_time"])
    df['date']  = df['publish_time'].dt.date
    df['day']  = df['publish_time'].dt.day
    df['hour'] = df['publish_time'].dt.hour
    print(df['hour'])
    
    # index = 列(Y軸), columns = 欄(X軸), values = 要計算的東西
    heatmap_data = df.pivot_table(index = 'date', 
                                  columns = 'hour',
                                  values = 'comment_count',
                                  aggfunc = "sum"
                                  # 統計方式，也可以傳入多個或自訂函數 aggfunc=[np.mean, np.sum, len]
                                  # sum、mean、median、max、min、std、len、
                                  )
    # fill null with 0
    heatmap_data = heatmap_data.fillna(0)
    print(heatmap_data)
    
    return heatmap_data

# 產製熱力圖資料 (三維分析)，有含無資料時間
def create_heatmap_data_fulltime(df):
        
    # 時間格式化
    df['publish_time'] = pd.to_datetime(df["publish_time"])
    df['date']  = df['publish_time'].dt.date
    df['day']  = df['publish_time'].dt.day
    df['hour'] = df['publish_time'].dt.hour
    print(df['hour'])
    
    # index = 列(Y軸), columns = 欄(X軸), values = 要計算的東西
    heatmap_data = df.pivot_table(index = 'date', 
                                  columns = 'hour',
                                  values = 'comment_count',
                                  aggfunc = "sum"
                                  # 統計方式，也可以傳入多個或自訂函數 aggfunc=[np.mean, np.sum, len]
                                  # sum、mean、median、max、min、std、len、
                                  )
    # 產製 x 軸完整小時刻度 (包含無資料的時間)
    ## 產製小時刻度 (0~23小時)
    full_hours = list(range(24))
    
    ## reindex 強制將無資料欄位塞入 0
    heatmap_data = heatmap_data.reindex(columns = full_hours, fill_value = 0)
    
    # 產製 y 軸完整日期刻度 (包含無資料的時間)
    ## 抓出最早和最晚的日期，以利產製中間刻度
    # min_date = df['date'].min()
    # max_date = df['date'].max()
    
    # ## 獲得此區間內所有日期
    # full_dates = pd.date_range(start = min_date, end = max_date, freq='D').date
    # ## reindex 強制將無資料欄位塞入 0
    # heatmap_data = heatmap_data.reindex(index = full_dates, fill_value = 0)
    
    ## x、y 軸刻度排序 
    ## ascending：True(升冪)、False(降冪)
    heatmap_data = heatmap_data.sort_index(axis = 0, ascending=False).sort_index(axis = 1, ascending=True)

    print(heatmap_data)
    
    return heatmap_data
    
# 產製【文章】包含指定 keyword、匹配指定時間
def article_contain_key(df, keywords, start_date, end_date):
    print(f"開始分析關鍵字：{'、'.join(target_keywords)}")
    # 複製一份資料
    df_temp = df.copy()
    
    # 過濾時間段
    df_temp['publish_time'] = pd.to_datetime(df_temp['publish_time'])
    
    ## 建立時間遮罩
    time_mask = (df_temp['publish_time'] >= start_date) & (df_temp['publish_time'] <= end_date)
    df_temp = df_temp[time_mask]
    
    # 建立篩選條件，從原始留言中找出包含指定字串的 series (列)
    
    ## 將輸入的關鍵字陣列轉為 regex 字串
    regex_pattern = "|".join(keywords)
    key_mask = df_temp['content_raw'].str.contains(regex_pattern, na=False, regex=True)
    # 套用篩選
    filtered_df = df_temp[key_mask].copy()
    
    # 標準化欄位
    # 取得時間來定義xy軸，強制(覆蓋)設定"comment_count" 為 1，代表「這篇文章出現了 1 次關鍵字」
    filtered_df['comment_count'] = 1
    
    # 只保留需要的欄位
    filtered_df = filtered_df[['publish_time', 'comment_count']]

    print(f"文章篩選完成：找到 {len(filtered_df)} 篇包含 '{keywords}' 的文章")
    return filtered_df

# 產製【留言】包含指定 keyword、匹配指定時間
def comments_contain_key(df, keywords, start_date, end_date):
    
    # 1.拷貝一份資料
    df_temp = df.copy()
    
    # 2.將巢狀結構炸開，list 結構會轉換為多列，將 x 則留言扁平化 
    ## 原本列數會從 len(json) 變為 (雖json + x)
    df_exploded = df_temp.explode("comments")
    
    ## 防呆：移除本身沒有留言的文章 (直接避免後續出現 NaN)
    df_exploded = df_exploded.dropna(subset = ["comments"])
        
    # 3.提取巢狀結構資料，找出目標欄位(內容、時間) 
    df_exploded['cmt_content'] = df_exploded["comments"].apply(lambda x: x.get("comment_content", "")) # 可能有多句
    df_exploded["cmt_time"] = df_exploded["comments"].apply(lambda x: x.get("comment_date_format"))
    
    ## 轉時間格式並改名 (方便後續過濾)
    df_exploded['publish_time'] = pd.to_datetime(df_exploded["cmt_time"])
    
    # 4.時間過濾
    time_mask = (df_exploded['publish_time'] >= start_date) & (df_exploded['publish_time'] <= end_date)
    df_exploded = df_exploded[time_mask]
    
    # 5.條件篩選，找出包含 keywords 的 series
    regex_pattern = "|".join(keywords)
    key_mask = df_exploded['cmt_content'].str.contains(regex_pattern, na=False, regex=True)
    filtered_comments = df_exploded[key_mask].copy()
    
    # 6.標準化
    ## 設定計數器為 1 ，只要有被選中的列就代表留言至少出現一次 (多次也以一次計)
    filtered_comments['comment_count'] = 1
       
    ## 只保留指定欄位
    filtered_comments = filtered_comments[['publish_time', 'comment_count']]
    
    print(f"留言篩選完成：找到 {len(filtered_comments)} 則包含 '{keywords}' 的留言")
    
    return filtered_comments

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
    for json_to_do in json_files:
        current_json_name = re.split(r'[/]+', json_to_do.replace( '\\', '/'))[-1]
        
        with open(json_to_do  , 'r', encoding='utf-8') as f:
            # json.load() 讀取檔案內容並解析成 Python 物件 (這裡會是個字典)
            article_json = json.load(f)
            
            # 把檔案名稱也存成dataframe 欄位
            article_json["source_filename"] = current_json_name
            json_list.append(article_json)


    df = pd.DataFrame(json_list)
    
    # 格式化使用者輸入的時間
    start_dt, end_dt = format_filter_time(data_start_date_str, data_end_date_str)

    # 產製文章、留言都 filter 關鍵字的 dataframe 
    df_article_filtered = article_contain_key(df, keywords=target_keywords, start_date=start_dt, end_date=end_dt )
    df_comment_filtered = comments_contain_key(df, keywords=target_keywords, start_date=start_dt, end_date=end_dt )
    df_keyword = pd.concat([df_article_filtered, df_comment_filtered], ignore_index=True)
    
    # 搜尋結果為空的處置
    if len(df_keyword) == 0:
        print("⚠️ 搜尋結果為空，無法繪圖。請檢查日期範圍或關鍵字 ( ´•̥̥̥ω•̥̥̥` ) ")
    else:
        # 產製熱力圖所需資料
        heatmap_data = create_heatmap_data_fulltime(df_keyword)
        
        plt.figure(figsize=(12, 6))

        # 繪製熱力圖
        sns.heatmap(heatmap_data, 
                    annot = True,  # 是否顯示格子上的數字
                    fmt='g',  # 數字格式 (general)，避免出現科學記號，fmt = 'd' 取到整數位(.1f = 小數一位)
                    cmap="Blues",  # 格子顏色，可選 Reds
                    linewidths=0.5,  # 格線寬度
                    linecolor='white' # 格線顏色
                    ) 
        # annot = True：要在格子上出現數字 fmt = 'd' 取到整數位(.1f = 小數一位)
        
        # 設定圖片標題
        keywords_str = "、".join(target_keywords)
        ## 避免關鍵字太多的省略
        if len(target_keywords) > 5:
            keywords_title = "、".join(target_keywords[:3]) + "..."
        else:
            keywords_title = keywords_str
        
        plt.title(f"關鍵字【{keywords_title}】時空聲量圖", 
                fontproperties=my_font, fontsize=14, pad=20) # pad: 標題跟圖表的距離
        
        # 設定 xy 軸名稱與屬性
        plt.xlabel("小時 (Hour)", fontproperties=my_font, fontsize=12)
        plt.ylabel("日期 (Date)", fontproperties=my_font, fontsize=12)
        
        # 圖片存檔
        plt.savefig(output_file_path , bbox_inches='tight', dpi = 300) 
        
        
        print(r"""
                    /\_/\
                = ( • . • ) =
                  /      \   完成了唷 =u=            
            """)
        print(f"視覺化過程共集結 {len(json_files)} 篇文章結果")
        print(f"輸出檔案路徑 = {output_file_path}")
        
        # 現場展圖
        plt.show()  # 務必在另存圖片之後，因為 show 結束後會把畫布清空
