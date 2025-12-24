import jieba
from collections import Counter
file_path = (r'/content/jiabaWord.txt')
jieba.load_userdict(file_path)

# 停用詞
skipWord = {
    '的', '了', '是', '和', '都', '就', '而', '及', '與', '著', "你", "我", "他","在", "但",
    '被', "也",
    '\n', ' ', '，', '。', '！', '？', "(", ")", "「", "」", "、" , "/","【","】", "--", "：", ":", "."
}

# 手動添加中文單詞到預設中文字庫裡
# jieba.add_word(word, freq=None, tag=None)

# 整體實作流程
# 輸入 (文章字串) -> 斷詞 (Cut) -> 清洗 (Filter) -> 統計 (Count) -> 輸出 (Top Keywords)

# ==== 1.輸入 (文章字串) ==== 
sentence = "獨家｜張文筆電硬碟破解卡關！電競SSD遭48數碼加密\u3000刑事局求助原廠碰壁試圖「暴力破解」\n\n知新聞 【記者林志青／台北報導】\n19日犯下台北捷運、中山商圈隨機攻擊案，造成3死11傷的張文（27歲）最後墜樓身亡。專案小組在張文公園路租屋處找到被燒毀的筆電，硬碟雖完好，送刑事局解密至今無下文。原因出在張文筆電是華碩電競品牌ROG在2023年推出的頂級電競筆電Strix SCAR 18 G834，硬碟為1TB起跳的SSD固態硬碟，採Windows 11預設「BitLocker」數位加密。專案小組經向原廠及微軟求助碰壁後，決定用「暴力破解」方式，逐一測試48字元數字密碼，相當於10的48次方，盼早日打開張文殺人的黑盒子。\n\n據悉，這款華碩ROG前年推出的電競筆電，屬於Strix系列，主打重度電競玩家及著重效能的玩家。擁有華麗的18吋 Nebula霓真技術電競螢幕及，採用2.5K 240Hz Mini LED面板；搭載英特爾i9 處理器 14900HX，輝達GeForce RTM 4090 顯示卡，Strix SCAR 18 擁有 64GB 的 DDR5 記憶體和 2TB 的 PCIe Gen4x4 儲存空間，輕鬆進行遊戲多工、串流直播和創作內容。\n\n華碩ROG Strix SCAR 18 G834最俗9萬5999元\n據瞭解，擁有32GB DDR5記憶體、2TB的PCIe Gen4 M.2 SSD的G834，上市約11萬9999元；16GB、1TB規格要價約9萬5999元。要價不菲的電競筆電如何購得，也是待解的謎團。\n\nWindows 11預設「BitLocker」數位加密\n關於加密難破解的SSD固態硬碟，乃是因為Windows 11預設「BitLocker」數位加密，如果硬碟離開主機板，或是BIOS/UEFI 更新，就會要求使用者輸入「BitLocker」修復金鑰，一組48字元的數字密碼，否則無法開啟硬碟。\n\n華碩、微軟均無法協助\u3000刑事局土法煉鋼「暴力破解」\n\n台北市刑大等專案小組19日晚上在張文公園路租屋處滅火後，找到這台被燒毀的華碩ROG電競筆電，雖然螢幕、主機板毀損，但SSD固態硬碟完好，但嘗試破解遇阻，雖然交給刑事局解析，但製造方的華碩及軟體方的微軟，均表示無法破解，刑事局最後決定採取「暴力破解」方式，透過軟體逐一測試可能的密碼，直到找出真正密碼，也就是跑完10的48次方組密碼就能順利讀取檔案。\n\n張文郵局帳戶餘額39元\u3000桃園母資助入不敷出\n專案小組另發現張文的金流相當單純，僅郵局一個，餘額僅剩39元，資金往來就是過去在台中任保全的薪資儲蓄，以及母親平均每月1萬餘元的資助。張文在公園路雅房租處每月房租要1萬7000元，今年1月居住至案發日，入不敷出最後坐吃山空，張文死後留下許多謎團待解。\n\n新聞連結：https://reurl.cc/k89qj3哪來的錢可以買一台快10萬的筆電啊\n\n--\nSent from nPTT on my iPhone 14 Pro Max\n\n--"

# ==== 2.斷詞 (Cut) ==== 
## 精確模式
segments = list(jieba.cut(sentence, cut_all = False))
print('精確模式')
# print(" | ".join(segments))

# ==== 3.清洗 (Filter) ==== 
wordClean = []
for word in segments:
    # 濾除：在預設跳脫字、空值或空白、一個字、純數字
    if (word not in skipWord) and (len(word.strip()) != 0) and (len(word) > 1) and (not word.isdigit()): 
        wordClean.append(word)
        # 將 wordClean 視為乾淨的文本

print('=======wordClean========')

# 將文本中的單字出現次數存為字典
counts = Counter(wordClean)

# 計算 Top(n)
popular = counts.most_common(20)


# 依照字 value 由大排序到小
# sorted_wordClean = sorted(popular.items(), reverse=True, key = lambda x:x[1])
# print(sorted_wordClean)

for i in range(len(popular)):
    print(f"{i + 1}. {popular[i][0]} ({popular[i][1]}次)")