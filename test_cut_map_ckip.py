import json
import re
import os # 處理路徑
from collections import Counter
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import glob


input_folder = r"json_test/PTT" 
output_folder = r"json_test/PTT/CKIP"
os.makedirs(output_folder, exist_ok=True)

json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本

top_n = 50 # 計算 Top(n) 自定義，包含 文章 和 留言總和

# 【選用】ckip 自定義字典權重 (分數越高越優先被解析出來)
word_to_weight = {
    "張文": 1,
    "加密貨幣": 1,
    "台北市政府": 1,
    "不知道": 1,
    "水喔": 1,
    "每次": 1,
}
dictionary = construct_dictionary(word_to_weight)
        
# === 載入ckip模型，並將WS, POS, NER定義為全域變數，供此程式內所有函數使用
class CkipProcessor:
    def __init__(self):
        catAscii = r"""
                /\_/\
            = ( • . • ) =
               /      \  等我一下就好唷 =u=    
        """
        # 1. 載入模型 (路徑指向 data 資料夾)
        # 這一步會花一點時間載入，且會佔用約 1-2GB 記憶體
        print("=" * 80)
        print("正在載入 CkipTagger 模型，約等待30秒，請稍候...(只會執行一次)")
        print(catAscii)
        print("=" * 80)
        
        self.ws = WS("./data", disable_cuda=False) # 斷詞
        self.pos = POS("./data", disable_cuda=False) # 詞性標註
        self.ner = NER("./data", disable_cuda=False) # 實體標註("普通"的名詞例如捷運不會被視為實體)
        print("=" * 80)
        print("模型載入完成！")
        print("=" * 80)
        
        return

    # 執行斷句，但尚未篩選有意義詞彙
    def execute_CkipCut(self, all_sentence_pool): # 投入已分割好的陣列
        
        # ⚠️ all_sentence_pool 內的每個物件原是【字串】，須轉為【陣列】(CKIP 規範)
        all_sentence_pool = [[str] for str in all_sentence_pool]

        # CkipTagger 接受的 input 必須是「列表 (List)」，即使只有一句話也要包成 List
        
        all_word_sentence_list = [] # 尚未篩選的斷詞大池子
        all_pos_sentence_list = [] # 尚未篩選的斷詞詞性大池子
        
        for sentence_list in all_sentence_pool:
            # 執行核心斷詞任務 
            # 斷詞 (Word Segmentation)
            word_sentence_list = self.ws(
                sentence_list,
                recommend_dictionary=dictionary
                # sentence_segmentation = True, # 是否考慮句子切分符號
                # segment_delimiter_set = {",", "。", ":", "?", "!", ";"} # 句子切分符號集合
            )

            all_word_sentence_list.append(word_sentence_list)

            # 詞性標註 (Part-Of-Speech Tagging)
            pos_sentence_list = self.pos(word_sentence_list)
            all_pos_sentence_list.append(pos_sentence_list )

            # 命名實體辨識 (Named Entity Recognition)
            # entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)

        # ⚠️ 須把結果陣列內的【陣列物件】解開為【字串】
        all_word_sentence_list = [item for sublist in all_word_sentence_list for item in sublist]
        all_pos_sentence_list =  [item for sublist in all_pos_sentence_list for item in sublist]
        
        print('解開後的 all_word_sentence_list = ',  all_word_sentence_list)
        
        return all_word_sentence_list, all_pos_sentence_list
    
# 篩選有意義的關鍵字 (尚未統計，裡面都是陣列，供 cursor 使用)
def filter_target_word(all_word_sentence_list, all_pos_sentence_list): # 篩選有意義
    
    # 斷句完成有意義的句子總和 (有意義但尚未統計，裡面都是陣列，供 cursor 使用)
    all_done_sentence = []

    # 要保留的目標詞性，基本上是 N開頭的名詞類 和 V開頭的動詞類
    # {'Na', 'Nb', 'Nc', 'Ncd', 'Nv', 'V'}

    for i in range(len(all_word_sentence_list)):
        target_word = []
        for word, tag in  zip(all_word_sentence_list[i],  all_pos_sentence_list[i]):
            if tag.startswith('N') or tag.startswith('V') : # 只選名詞和動詞
                if len(word) > 1: # 濾除一個字以下的
                    target_word.append(word)
        
        all_done_sentence.append(target_word)

    return all_done_sentence


# 斷詞前預處理 (json讀取結果 > 大池子)
def article_to_cursorMap(article_json):
    task_map = [] # 斷詞執行數量
    all_sentence_pool = [] # 準備斷句的大池子

    # 分割文章為句子陣列，\s 匹配空格、Tab (\t)、換行符 (\n) 等
    a_sentence = re.split(r'[,，。;；!！?？\s]', article_json["content_raw"]) 
    a_sentence_list = [s.strip() for s in a_sentence if len(s.strip()) > 0] # 移除陣列中的空字串

    print(f"原始文章被分割成 {len(a_sentence_list)} 個句子")
    print("=" * 80)
    task_map.append(len(a_sentence_list))
    # 裝入另一個清單所有內容
    all_sentence_pool.extend(a_sentence_list)

    # == 處理留言 ==
    sentence_loop = article_json["comments"]
    for i in range(len(sentence_loop)):
        c_sentence = re.split(r'[,，。;；!！?？\s]', sentence_loop[i]["comment_content"]) 
        c_sentence_list = [s.strip() for s in c_sentence if len(s.strip()) > 0] # 移除陣列中的空字串
        task_map.append(len(c_sentence_list))
        all_sentence_pool.extend(c_sentence_list)

    print("task_map = ", task_map) # cursor
    print("=" * 80)
    print("all_sentence_pool = ", all_sentence_pool) # 文章 + 大池子，已事先斷句完成
    print(f" all_sentence_pool 總共有 {len(all_sentence_pool)} 句")
    
    return task_map, all_sentence_pool

# Cursor 回填 + 放進待統計大池子 (清單數 = 留言總數 + 1文章 )
def cursor_mapping(all_done_sentence):
    list_to_count = []

    print("len(task_map) = ", len(task_map))

    map_cursor = 0
    for i in range(len(task_map)):
        merge_this_sentence = []
        for j in all_done_sentence[map_cursor: map_cursor + task_map[i]]:
            merge_this_sentence.extend(j) # 組回該文章或留言的完整斷句結果

        list_to_count.append(merge_this_sentence) # 將完整斷句結果加回待分配給 json 的清單 (總句數會是 文章總留言數 + 1篇文章)
        map_cursor += task_map[i]
            

    print("cursor 結果驗證：")
    print("主文章 + 留言共有",  len(article_json["comments"]) + 1,"個物件數")
    print("list_to_count (待分配回 json 的清單) 共有", len(list_to_count), "個清單數")
    print("list_to_count = ", list_to_count)
    
    return list_to_count

# Counter 統計輿情 +  寫入偽 json
def counter_result(list_to_count):
    
    # 留言統計 ( 拆解為扁平陣列結構才能給 count)
    word_to_count = [str(item) for word_list in list_to_count[1:] for item in word_list]
    comment_counts = Counter(word_to_count)
    comment_popular = comment_counts.most_common(top_n)
    print("comment_popular = ", comment_popular)

    ## === (檢查用)依照字 value 由大排序到小
    print(f'檢查 top {top_n} 留言關鍵字')
    for i in range(len(comment_popular)):
        print(f"{i + 1}. {comment_popular[i][0]} ({comment_popular[i][1]}次)")

    ## 文章的 top 結果
    content_counts = Counter(list_to_count[0])
    content_popular = content_counts.most_common(top_n)
    print("content_popular =", content_popular )

     ## === (檢查用)依照字 value 由大排序到小
    print(f'檢查 top {top_n} 文章關鍵字')
    for i in range(len(content_popular)):
        print(f"{i + 1}. {content_popular[i][0]} ({content_popular[i][1]}次)")

    # 寫入文章 top n、留言總和 top n
    article_json["content_keywords"] = content_popular # 文章斷詞 Top n 結果
    article_json["comments_top_key"] = comment_popular # 所有留言 top n結果

    # 依序寫入留言關鍵字結果 (已 cursor 完成)
    for i in range(len(list_to_count) - 1):
        article_json["comments"][i]["comment_keywords"] = list_to_count[i + 1]

    return article_json

# === 主程式
if __name__ == "__main__":   
    
    for json_to_do in json_files:
        
        current_json_name = re.split(r'[/]+', json_to_do.replace( '\\', '/'))[-1]
        print(current_json_name)
        print(type(current_json_name))
        output_file_path = os.path.join(output_folder, current_json_name) # 分析完成的 json，輸出路徑
        
        print(f"正在分析文章：【{current_json_name}】")
        
        # 1. 載入文章，先存起來，最後要儲存結果時再打開
        print("=" * 80)
        print("正在執行程序：1. 載入文章 ")
        print("=" * 80)
        with open(json_to_do  , 'r', encoding='utf-8') as f:
            # json.load() 讀取檔案內容並解析成 Python 物件 (這裡會是個字典)
            article_json = json.load(f)
        
        # 2. 讀取文章加入大池子 
        print("=" * 80)
        print("正在執行程序：2. 讀取文章加入大池子 ")
        print("=" * 80)
        task_map, all_sentence_pool = article_to_cursorMap(article_json) 
            
        
        # 3.初始化並執行斷詞 (載入模型，只跑一次)
        print("=" * 80)
        print("正在執行程序：3.初始化並執行斷詞 ")
        print("=" * 80)
        processor = CkipProcessor()
        all_word_sentence_list, all_pos_sentence_list = processor.execute_CkipCut(all_sentence_pool)

        
        # 4. 篩選有意義的關鍵字 (尚未統計，裡面都是陣列，供 cursor 使用)
        print("=" * 80)
        print("正在執行程序：4. 篩選有意義的關鍵字 ")
        print("=" * 80)
        all_done_sentence = filter_target_word(all_word_sentence_list, all_pos_sentence_list)
    
        # 5. Cursor 回填 + 放進待統計大池子 (清單數 = 留言總數 + 1文章 )
        print("=" * 80)
        print("正在執行程序：5. Cursor 回填 + 放進待統計大池子 ")
        print("=" * 80)
        list_to_count = cursor_mapping(all_done_sentence)
        
        # 6. Counter 統計輿情 +  寫入偽 json
        print("=" * 80)
        print("正在執行程序：6. Counter 統計輿情 +  寫入偽 json ")
        print("=" * 80)
        article_json = counter_result(list_to_count)
        
        # 99. 返還 Json 結果
        print("=" * 80)
        print("Fianl：待寫入的 Json")
        print("=" * 80)
        pretty_json = json.dumps(article_json, indent=4, ensure_ascii=False)
        print(pretty_json)
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # json.dump(obj, fp, indent=4) 參數可以讓輸出的 JSON 更易讀
            json.dump(article_json, f, ensure_ascii=False, indent=4)

    