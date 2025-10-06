import pandas as pd
import jieba
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# 自動偵測中文字型
def get_font_path():
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",   # Ubuntu / Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK.ttc",           # 另一種 Linux
        "/System/Library/Fonts/STHeiti Medium.ttc",                 # macOS
        "C:/Windows/Fonts/msjh.ttc",                                # Windows 微軟正黑體
        "C:/Windows/Fonts/simhei.ttf",                              # Windows 黑體
        "TaipeiSansTCBeta-Regular.ttf"                              # 專案目錄自帶字型
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("⚠️ 找不到中文字型，請安裝 Noto Sans CJK 或放一個 TTF 檔在專案目錄裡")

# 讀取資料
df = pd.read_csv("ptt_stock_articles.csv")

# 基礎統計
df["互動總數"] = df["推文數量"] + df["噓文數量"] + df["箭頭數量"]
print("最熱門文章：")
print(df.sort_values("互動總數", ascending=False).head())

# 詞頻分析
text = " ".join(df["內文"].astype(str))
words = jieba.lcut(text)
word_counts = Counter(words)

# 停用詞
stopwords = set(["的", "了", "是", "在", "我", "有", "就", "不", "也", "人", "都", "還"])
filtered = {w: c for w, c in word_counts.items() if w not in stopwords and len(w) > 1}

print("高頻詞：", Counter(filtered).most_common(20))

# ===== 產生詞雲 =====
font_path = get_font_path()
wc = WordCloud(
    font_path=font_path,
    width=800,
    height=400,
    background_color="white"
)
wc.generate_from_frequencies(filtered)

plt.figure(figsize=(10, 5))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.tight_layout()
plt.savefig("wordcloud.png", dpi=300)
print("✅ 詞雲已存成：wordcloud.png")

# ===== 推/噓比例長條圖 =====
plt.figure(figsize=(8, 6))
counts = [df["推文數量"].sum(), df["噓文數量"].sum(), df["箭頭數量"].sum()]
labels = ["推文", "噓文", "箭頭"]

plt.bar(labels, counts, color=["green", "red", "gray"])
plt.title("PTT Stock 版 推/噓/箭頭 總數量")
plt.ylabel("數量")
plt.tight_layout()
plt.savefig("push_boo_chart.png", dpi=300)
print("✅ 推噓文比例長條圖已存成：push_boo_chart.png")

plt.show()
