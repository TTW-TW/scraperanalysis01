import re
from collections import Counter
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER

catAscii = r"""
    /\_/\
= ( • . • ) =
   /      \      
"""
# 1. 載入模型 (路徑指向 data 資料夾)
# 這一步會花一點時間載入，且會佔用約 1-2GB 記憶體
print("=" * 80)
print("正在載入 CkipTagger 模型，約等待30秒，請稍候...")
print(catAscii)
print("=" * 80)

ws = WS("./data") # 斷詞
pos = POS("./data") # 詞性標註
ner = NER("./data") # 實體標註("普通"的名詞例如捷運不會被視為實體)
print("=" * 80)
print("模型載入完成！")
print("=" * 80)

# 2. 準備測試文字
# CkipTagger 接受的 input 必須是「列表 (List)」，即使只有一句話也要包成 List

origin_article = "1.媒體來源:\n匯流新聞網\n\n2.記者署名:\n記者張孝義\n\n3.完整新聞標題:\n隨機攻擊案遭割喉蕭姓騎士未獲任何保險 UG董座案發秒捐百萬送暖\n\n4.完整新聞內文:https://i.imgur.com/axAH3N7.jpeg台北市中山捷運站周邊1219隨機攻擊事件，造成4死11傷，不幸遭凶嫌割喉身亡的蕭姓騎士\n，家屬僅能申請犯罪被害人保護補償金180萬元，台北市政府積極募款；連鎖茶飲品牌UG董\n事長鄭凱隆手提自家飲料與花束到案發現場致意，被外界質疑藉悼唁行銷品牌，其實在負面\n新聞出現之前，鄭凱隆就低調表達捐款意願，並於第一時間匯款百萬元指定捐助蕭姓騎士。\n\n1219隨機攻擊事件發生後，市府立即啟動跨局處應變機制，逐一關懷訪視受害者及家屬，協\n助處理醫療、喪葬與後續生活支持事宜，市長蔣萬安指示社會局局長姚淑文積極募款捐助受\n害者，尤其是不幸身亡的蕭姓機車騎士，因事發地點無法獲得相關保險。姚淑文費心向各企\n業募款時，接到UG聯發國際董事長鄭凱隆主動表示願意捐款給蕭的家人。\n\n姚淑文在友人的line群組表示，面對1219的襲擊事件，市府沒有一個人敢懈怠，除了關懷訪\n問每一個受害家屬，知道他們的需求，更重要的是幫忙承擔每一個傷亡者的醫療、喪葬和慰\n撫金。事件是突發狀況，沒有所謂的預算來因應，更多時候需要對外募款。她記得從最後一\n家醫院出來時，市長指示能夠幫忙的就幫忙，需要募款也要快。\n\n37歲的蕭姓男子當時騎車經過現場，因禮讓行人而遭凶嫌揮刀砍殺身亡，案發地點既非捷運\n站、也非百貨商場，成為此次事件「唯一無法獲得保險賠償」的被害者。\n\n姚淑文在文中表示，蕭姓機車騎士是家中主要經濟來源，市長指示社會局須設法協助，並評\n估對外募款的必要性。她也記錄當時與鄭凱隆的通話內容指出，當她向鄭凱隆說明該名被害\n人的特殊處境時，曾直接詢問：「董事長，如果可行，可以指定捐款給這位被害人嗎？」鄭\n凱隆當下即回應願意協助，並表示「可以做到的」。\n\n文中進一步提到，隔週一上班日，銀行一開門，社會局即收到一筆新台幣100萬元的匯款。\n姚淑文形容這筆善款對她而言，代表的是在最需要資源的時刻，對受害家屬提供了即時且實\n質的支持，因此特別表達感謝之意。\n\n台北市政府啟動職災與保險機制協助受害者，社會局表示將設立「1219事件」愛心捐款平台\n，接受民眾愛心捐款。所有捐款均依照既有社福流程協助媒合與處理，確保受害者及其家屬\n獲得必要支持。\n\n5.完整新聞連結 (或短網址)不可用YAHOO、LINE、MSN等轉載媒體:https://cnews.com.tw/224251223a02/6.備註:\n\n看到炎上的UG老闆捐了一百萬\n給最弱勢沒保險的那位受害騎士\n相較於拿飲料的無心之過 捐錢才是真的\n個人覺得他也道歉了 沒必要獵巫\n不如想想怎麼防止第二個張文的出現吧\n\n\n--"
sentence_list = re.split(r'[,，。;；!！?？\n]', origin_article) # 分割文章為句子陣列
sentence_list = [s.strip() for s in sentence_list if len(s.strip()) > 0] # 移除陣列中的空字串

print(f"原始文章被分割成 {len(sentence_list)} 個句子")


# 自定義字典權重 (分數越高越優先被解析出來)
word_to_weight = {
    "張文": 1,
    "加密貨幣": 1,
    "台北市政府": 1
    
}
dictionary = construct_dictionary(word_to_weight)


# 3. 執行核心斷詞任務 

# 斷詞 (Word Segmentation)
word_sentence_list = ws(
    sentence_list,
    recommend_dictionary=dictionary
    # sentence_segmentation = True, # 是否考慮句子切分符號
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"} # 句子切分符號集合
)

# 詞性標註 (Part-Of-Speech Tagging)
pos_sentence_list = pos(word_sentence_list)

# 命名實體辨識 (Named Entity Recognition)
entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

# 4. 展示結果
WS_list = []
POS_tag_list = []
NER_list = []
print("\n" + "="*40)
for i, sentence in enumerate(sentence_list):
    print(f"原文: {sentence}")
    # 印出斷詞結果
    print(f"斷詞: {word_sentence_list[i]}")
    # 印出詞性
    print(f"詞性: {pos_sentence_list[i]}")
    # 印出實體 (人名、地名、組織...)
    print("實體辨識:")
    for entity in entity_sentence_list[i]:
        print(f"    {entity}")
    print("-" * 40)

# 5. 詞頻統計

target_word = []


# 要保留的目標詞性，基本上是 N開頭的名詞類 和 V開頭的動詞類
target_pos = {'Na', 'Nb', 'Nc', 'Ncd', 'Nv', 'V'}

for i in range (len(word_sentence_list)):
    words = word_sentence_list[i]
    postags = pos_sentence_list[i]
    
    # zip組合成字典後進行清理
    for word, tag in  zip(words, postags):
        if tag.startswith('N') or tag.startswith('V') : # 只選名詞和動詞
           if len(word) > 1: # 濾除一個字以下的
               target_word.append(word)
       
print('=' * 80 ) 
print(" ".join(target_word)) 
print('=' * 80 )  
## 熱門關鍵字
top_n = 20
counter = Counter(target_word)
print(f'=========熱門關鍵字 (Top {top_n})==========')
popular = counter.most_common(20)

for i in range(len(popular)):
    print(f"{i + 1}. {popular[i][0]} ({popular[i][1]}次)")

## 實體辨識結果
print('=========實體辨識結果==========')







# 釋放記憶體 (在真實專案中，如果不需再用建議刪除以節省資源)
# del ws, pos, ner