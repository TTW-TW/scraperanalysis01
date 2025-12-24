import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud

mask_path = r''
font_path = r'font/Iansui-Regular.ttf'

mask = np.array(Image.open(r"content/wordCloudMask/taiwan.jpg"))
with open(r'content/wordCloud_article.txt', 'r', encoding='utf-8') as file:
        zh_news = file.read()

# 文字雲基本參數
# width, height
wordcloud = WordCloud(mask = mask , margin = 1, scale = 2, contour_color="#A4A7A5", contour_width=3, background_color = "black", colormap = "Set3", max_words = 80, min_font_size = 8, font_path = font_path ).generate(zh_news)

# 遮罩圖片參數

# 繪圖
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()