import json
import re
import os # 處理路徑
from collections import Counter
import jieba
import glob

jieba_file_path = (r'content/jiabaWord.txt')
jieba.load_userdict(jieba_file_path)

file_path = r"json_test/PTT/邊緣_誰會凸兔兔.json"
input_folder = r"json_test/PTT" 
output_folder = r"json_test/PTT/Jieba"
os.makedirs(output_folder, exist_ok=True)

json_files = glob.glob(os.path.join(input_folder, '*.json')) # 所有待分析的原始文本

top_n = 50 # 計算 Top(n) 自定義，包含 文章 和 留言總和

# 停用詞
skipWord = {
    '的', '了', '是', '和', '都', '就', '而', '及', '與', '著', "你", "我", "他","在", "但", '被', "也", 
    '可以', '真的', '不錯', '應該', '不然', '然後', '自己', '就是', '除了', '好像', '不是', '還是',
    '只有', '可能', '現在', '一樣', '只能', '謝謝', '不會', '少來', '一下', '不要', '建議', '看看',
    '聽說', '只是', '只好', '還有', '還會', '很多', '沒有', '其他', '知道', '大家', '左右', '不用',
    '似乎', '疑似', '貌似', '不行', '但是', '可是', '很想', '超想', '很多', '很好', '那麼' , '已經',
    '以上', '以下', '大約', '所以', '所有', '全部', '如果', '假如', '大概', '大約', '無論', '怎樣',
    '到底', '究竟', '什麼', '因為', '覺得', '無論', '基本上', '這裡', '這些', '那些', '這個', '這樣',
    '一直', '一定', '本來', '這邊', '那邊', '這種', '那種', '怎麼', '怎麼辦', '有人', '而已', '這麼',
    '不過', '其實', '還能', '而是', '或是', '或者', '把特', '而且', '並且', '真是', '這是',
    '是不是', '有沒有', '對不對', '對吧', '一堆', '感覺', '直接', '當天', '當時', '那時',
    '趕快', '盡量', '繼續', '最後', '只會', '沒差', '一起', '當初', '當時', '反正', '反而', '反倒是', '反倒',
    '一點', '我們', '會不會', '還在', '這誰', '這哪位', '哪位', '這次', '當然', '必然', '這位',
    '以及', '甚至', '相當', '反而', '至少', '雖然', '竟然', '居然', '還好', '幸好', '所幸',
    '近期', '最近', '今天',  '今年', '明年', '去年', '這回', '之前', '原先', '原本', '原來', '近期', 
    '版主', '版大', '版主', '原Po', '原po',  '推推', '各位', '安安',
    '哈哈', '笑死', 'XD', 'XDD', 'XDDD', 'QQ', 'qq', 'xd', '嘻嘻', '呵呵', '顆顆', 
    '\n', ' ', '，', '。', '！', '？', "(", ")", "「", "」", "、" , "/","【","】", "--", "：", ":",
    ".",  '...', '..', 
    'https', 'http', 'www', '.tw' '//', 'com', 'imgur', 'jpeg', 'png', 'gif', 'jpg', 'svg'
}



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

    
# 批次執行結巴斷詞、篩選有意義並加入完成斷詞大池子
def execute_JiebaCut(all_sentence_pool):
    
    all_done_sentence = [] # 斷句完成的句子總和 (尚未統計，裡面都是陣列，供 cursor 使用)

    for sentence in all_sentence_pool:
        # ==== 3-2.斷詞 (Cut) ==== 
        ## 精確模式
        segments = list(jieba.cut(sentence, cut_all = False))

        # ==== 3-3.清洗 (Filter) ====  
        wordClean_this_sentence = []
        for word in segments:
            # 濾除：在預設跳脫字、空值或空白、一個字、純數字、NULL
            if (word not in skipWord) and (len(word.strip()) != 0) and (len(word) > 1) and (not word.isdigit()): 
                wordClean_this_sentence.append(word)
                # 將 wordClean 視為乾淨的文本
        all_done_sentence.append(wordClean_this_sentence)    
        
    return all_done_sentence
    

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

    # 寫入文章原始斷詞、文章 top n、留言總和 top n
    article_json["content_keywords"] = list_to_count[0]
    article_json["content_top_key"] = content_popular # 文章斷詞 Top n 結果
    article_json["comments_top_key"] = comment_popular # 所有留言 top n結果

    # 依序寫入留言關鍵字結果 (已 cursor 完成)
    for i in range(len(list_to_count) - 1):
        article_json["comments"][i]["comment_keywords"] = list_to_count[i + 1]

    return article_json

# === 主程式
if __name__ == "__main__":   
    
    for json_to_do in json_files:
        
        current_json_name = re.split(r'[/]+', json_to_do.replace( '\\', '/'))[-1]
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
            
        
        # 3.批次執行結巴斷詞、篩選有意義並加入完成斷詞大池子
        print("=" * 80)
        print("正在執行程序：3.批次執行結巴斷詞 ")
        print("=" * 80)
        all_done_sentence = execute_JiebaCut(all_sentence_pool)

        # 4. Cursor 回填 + 放進待統計大池子 (清單數 = 留言總數 + 1文章 )
        print("=" * 80)
        print("正在執行程序：4. Cursor 回填 + 放進待統計大池子 ")
        print("=" * 80)
        list_to_count = cursor_mapping(all_done_sentence)
        
        # 5. Counter 統計輿情 +  寫入偽 json
        print("=" * 80)
        print("正在執行程序：5. Counter 統計輿情 +  寫入偽 json ")
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

    print(r"""
                /\_/\
            = ( • . • ) =
               /      \   完成了唷 =u=            
        """)
    print(f"共分析 {len(json_files)} 篇文章")
    print(f"輸出檔案路徑 = {output_file_path}")