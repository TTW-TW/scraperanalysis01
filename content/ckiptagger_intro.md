
## 導入範例

```python
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
```

## 為斷詞提供您想特別關注的詞彙及它們的相對權重.

```python
word_to_weight = {
    "土地公": 1,
    "土地婆": 1,
    "公有": 2,
    "": 1,
    "來亂的": "啦",
    "緯來體育台": 1,
}
dictionary = construct_dictionary(word_to_weight)
print(dictionary)
```


## 實體類別列表

| Type	| Description	| 中文 |
|  ----  | ----  |----  |
| GPE	| Countries, cities, states	| 行政區| 
| PERSON	| People, including fictional	| 人物 |
| DATE	| Absolute or relative dates or periods	| 日期 |
| ORG	| Companies, agencies, institutions, etc.	| 組織 |
| CARDINAL |	Numerals that do not fall under another type	| 數字 |
| NORP	| Nationalities or religious or political groups	| 民族、宗教、政治團體 |
| LOC	| Non-GPE locations, mountain ranges, bodies of water	| 地理區 |
| TIME	| Times smaller than a day	 | 時間|
| FAC	| Buildings, airports, highways, bridges, etc.	| 設施 |
| MONEY	| Monetary values, including unit	| 金錢 |
| ORDINAL |	“first”, “second”	| 序數
| EVENT	| Named hurricanes, battles, wars, sports events, etc.	| 事件 |
| WORK_OF_ART	| Titles of books, songs, etc.	| 作品 |
| QUANTITY	| Measurements, as of weight or distance	| 數量 |
| PERCENT	| Percentage (including “%”)	| 百分比率 |
| LANGUAGE |	Any named language	| 語言 |
| PRODUCT |	Vehicles, weapons, foods, etc. (Not services)	| 產品 |
| LAW	| Named documents made into laws	| 法律 |

## 詞性列表

| Type                | Description |
|---------------------|-------------|
| A                   | 非謂形容詞       |
| Caa                 | 對等連接詞       |
| Cab                 | 連接詞，如：等等    |
| Cba                 | 連接詞，如：的話    |
| Cbb                 | 關聯連接詞       |
| D                   | 副詞          |
| Da                  | 數量副詞        |
| Dfa                 | 動詞前程度副詞     |
| Dfb                 | 動詞後程度副詞     |
| Di                  | 時態標記        |
| Dk                  | 句副詞         |
| DM                  | 定量式         |
| I                   | 感嘆詞         |
| Na                  | 普通名詞        |
| Nb                  | 專有名詞        |
| Nc                  | 地方詞         |
| Ncd                 | 位置詞         |
| Nd                  | 時間詞         |
| Nep                 | 指代定詞        |
| Neqa                | 數量定詞        |
| Neqb                | 後置數量定詞      |
| Nes                 | 特指定詞        |
| Neu                 | 數詞定詞        |
| Nf                  | 量詞          |
| Ng                  | 後置詞         |
| Nh                  | 代名詞         |
| Nv                  | 名物化動詞       |
| P                   | 介詞          |
| T                   | 語助詞         |
| VA                  | 動作不及物動詞     |
| VAC                 | 動作使動動詞      |
| VB                  | 動作類及物動詞     |
| VC                  | 動作及物動詞      |
| VCL                 | 動作接地方賓語動詞   |
| VD                  | 雙賓動詞        |
| VF                  | 動作謂賓動詞      |
| VE                  | 動作句賓動詞      |
| VG                  | 分類動詞        |
| VH                  | 狀態不及物動詞     |
| VHC                 | 狀態使動動詞      |
| VI                  | 狀態類及物動詞     |
| VJ                  | 狀態及物動詞      |
| VK                  | 狀態句賓動詞      |
| VL                  | 狀態謂賓動詞      |
| V_2                 | 有           |
| DE                  | 的之得地        |
| SHI                 | 是           |
| FW                  | 外文          |
| COLONCATEGORY       | 冒號          |
| COMMACATEGORY       | 逗號          |
| DASHCATEGORY        | 破折號         |
| DOTCATEGORY         | 點號          |
| ETCCATEGORY         | 刪節號         |
| EXCLAMATIONCATEGORY | 驚嘆號         |
| PARENTHESISCATEGORY | 括號          |
| PAUSECATEGORY       | 頓號          |
| PERIODCATEGORY      | 句號          |
| QUESTIONCATEGORY    | 問號          |
| SEMICOLONCATEGORY   | 分號          |
| SPCHANGECATEGORY    | 雙直線         |
| WHITESPACE          | 空白          |
