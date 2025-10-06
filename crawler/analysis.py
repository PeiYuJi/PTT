import pandas as pd
import jieba
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 讀取資料
df = pd.read_csv("ptt_stock_articles.csv")

# 基礎統計
df["互動總數"] = df["推文數量"] + df["噓文數量"] + df["箭頭數量"]
print("最熱門文章：")
print(df.sort_values("互動總數", ascending=False).head())

# 詞頻分析（內文斷詞）
text = " ".join(df["內文"].astype(str))
words = jieba.lcut(text)
word_counts = Counter(words)

# 移除停用詞
stopwords = set(["的", "了", "是", "在", "我", "有", "就", "不"])
filtered = {w:c for w,c in word_counts.items() if w not in stopwords and len(w)>1}

# 取前 20 個高頻詞
print("高頻詞：", Counter(filtered).most_common(20))

# 詞雲
wc = WordCloud(font_path="TaipeiSansTCBeta-Regular.ttf", width=800, height=400, background_color="white")
wc.generate_from_frequencies(filtered)
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.show()
