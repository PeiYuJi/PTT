import os
import re
import urllib.request
import zipfile
import pandas as pd
import jieba
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from wordcloud import WordCloud

# ===== 字型設定 =====
font_dir = "./fonts"
os.makedirs(font_dir, exist_ok=True)
font_path = os.path.join(font_dir, "NotoSansCJK-Regular.ttc")

if not os.path.exists(font_path):
    print("📥 正在下載 Noto 中文字型...")
    url = "https://noto-website-2.storage.googleapis.com/pkgs/NotoSansCJKtc-hinted.zip"
    zip_path = os.path.join(font_dir, "NotoSansCJKtc.zip")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(font_dir)
    os.remove(zip_path)
    for file in os.listdir(font_dir):
        if file.endswith(".ttc"):
            font_path = os.path.join(font_dir, file)
            break
    print(f"✅ 字型已下載並設置：{font_path}")

my_font = font_manager.FontProperties(fname=font_path)
rcParams["font.sans-serif"] = [font_path]
rcParams["axes.unicode_minus"] = False

# ===== 讀取資料 =====
df = pd.read_csv("output/ptt_stock_articles.csv")
df[["推文數量", "噓文數量", "箭頭數量"]] = df[["推文數量", "噓文數量", "箭頭數量"]].fillna(0)
df["互動總數"] = df["推文數量"] + df["噓文數量"] + df["箭頭數量"]

print("最熱門文章：")
print(df.sort_values("互動總數", ascending=False).head())

# ===== 選擇熱門文章 =====
# 以互動總數前10%為熱門文章
threshold = df["互動總數"].quantile(0.9)
df_hot = df[df["互動總數"] >= threshold]

# ===== 清理內文 =====
def clean_text(text):
    text = re.sub(r"\d{1,4}[/-]\d{1,2}[/-]\d{1,2}", " ", text)  # 日期
    text = re.sub(r"\d{1,2}:\d{2}", " ", text)                  # 時間
    text = re.sub(r"[0-9]+", " ", text)                         # 數字
    text = re.sub(r"[A-Za-z]+", " ", text)                     # 英文字母
    return text

df_hot["內文_clean"] = df_hot["內文"].astype(str).apply(clean_text)
text = " ".join(df_hot["內文_clean"])
words = jieba.lcut(text)
word_counts = Counter(words)

# ===== 停用詞設定 =====
stopwords = set([
    "的","了","是","在","我","有","就","不","也","人","都","還",
    "與","與其","被","你","他","她","我們","自己","這","那"
])

# 動態偵測高頻無意義詞
total_unique_words = len(word_counts)
top_percent = 0.01
num_top = max(1, int(total_unique_words * top_percent))
sorted_words = word_counts.most_common()
high_freq_words = [w for w, c in sorted_words[:num_top] if len(w) <= 2]
stopwords.update(high_freq_words)

filtered = {w: c for w, c in word_counts.items() if w not in stopwords and len(w) > 1}

print("熱門文章高頻詞：", Counter(filtered).most_common(20))
print(f"自動加入停用詞（前1%高頻短詞）：{high_freq_words}")

# ===== 產生熱門文章詞雲 =====
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
plt.savefig("hot_wordcloud.png", dpi=300)
print("✅ 熱門文章詞雲已存成：hot_wordcloud.png")

# ===== 推/噓/箭頭比例長條圖 =====
plt.figure(figsize=(8, 6))
counts = [df["推文數量"].sum(), df["噓文數量"].sum(), df["箭頭數量"].sum()]
labels = ["推文", "噓文", "箭頭"]
colors = ["green", "red", "gray"]

bars = plt.bar(labels, counts, color=colors)
for bar, count in zip(bars, counts):
    plt.text(bar.get_x() + bar.get_width()/2, count + max(counts)*0.01, str(int(count)),
             ha='center', fontproperties=my_font)

plt.title("PTT Stock 版 推/噓/箭頭 總數量", fontproperties=my_font)
plt.ylabel("數量", fontproperties=my_font)
plt.tight_layout()
plt.savefig("push_boo_chart.png", dpi=300)
print("✅ 推噓文比例長條圖已存成：push_boo_chart.png")

plt.show()
