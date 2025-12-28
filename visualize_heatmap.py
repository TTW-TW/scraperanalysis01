import json
import re
import os # 處理路徑
import glob
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import datetime


now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d%H%M%S")

input_folder = r"json_test/PTT/CKIP" 
output_folder = r"json_test/PTT/CKIP/Visualize" 
output_filename = f"heatmap_result_{timestamp_str}.png"
os.makedirs(output_folder, exist_ok=True)
output_file_path = os.path.join(output_folder, output_filename)


json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本
json_list = []
# df = pd.DataFrame(json_list)

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

# 產製熱力圖資料 (三維分析)，不含無資料時間
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
    heatmap_data = heatmap_data.sort_index(axis = 0).sort_index(axis = 1)

    print(heatmap_data)
    
    return heatmap_data
    
# 繪製特定關鍵字熱力圖


# === 主程式
if __name__ == "__main__":  
    # 產製熱力圖所需資料
    heatmap_data = create_heatmap_data_fulltime(df)

    # 繪製熱力圖
    sns.heatmap(heatmap_data, annot = False,  fmt='g', cmap="Blues", linewidths=0.5 ) 
    # annot = True：要在格子上出現數字 fmt = 'd' 取到整數位(.1f = 小數一位)
    
    # 圖片存檔
    plt.savefig(output_file_path , bbox_inches='tight', dpi = 300) 
    
    
    print(r"""
                /\_/\
            = ( • . • ) =
               /      \   完成了唷 =u=            
        """)
    print(f"視覺化過程共集結 {len(json_files)} 篇文章結果")
    print(f"輸出檔案路徑 = {output_file_path}")
    
    plt.show()  # 務必在另存圖片之後，因為 show 結束後會把畫布清空
