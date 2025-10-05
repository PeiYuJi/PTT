import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 設定 headers，模擬瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'cookie': 'over18=1'
}

BASE_URL = "https://www.ptt.cc/bbs/Stock/index.html"
PAGE_LIMIT = 10

data = []

# 先取得最新頁的 URL
res = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
# 找上一頁連結，取 index 編號
prev_link = soup.find('a', string='‹ 上頁')['href']
index_num = int(prev_link.split('index')[1].split('.html')[0]) + 1

for i in range(PAGE_LIMIT):
    page_url = f"https://www.ptt.cc/bbs/Stock/index{i + index_num}.html"
    res = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.find_all('div', class_='r-ent')

    for article in articles:
        # 有些文章被刪除會沒有 a 標籤
        a_tag = article.find('a')
        if a_tag:
            title = a_tag.text.strip()
            link = "https://www.ptt.cc" + a_tag['href']
            author = article.find('div', class_='author').text.strip()
            date = article.find('div', class_='date').text.strip()

            # 進入文章頁抓內文和推文
            res_art = requests.get(link, headers=headers)
            art_soup = BeautifulSoup(res_art.text, 'html.parser')

            main_content = art_soup.find('div', id='main-content')
            # 移除所有推文、meta 資訊
            for tag in main_content.find_all(['div', 'span'], class_=['article-metaline', 'article-metaline-right', 'push']):
                tag.extract()
            content = main_content.text.strip()

            # 統計推文數
            pushes = art_soup.find_all('div', class_='push-tag')
            print(art_soup)
            push_count = sum(1 for p in pushes if '推 ' in p.find('span', class_='push-tag').text)
            boo_count = sum(1 for p in pushes if '噓 ' in p.find('span', class_='push-tag').text)
            arrow_count = sum(1 for p in pushes if '→ ' in p.find('span', class_='push-tag').text)

            data.append({
                'title': title,
                'author': author,
                'date': date,
                'content': content,
                '推': push_count,
                '噓': boo_count,
                '→': arrow_count
            })

    time.sleep(0.5)  # 避免被擋

# 存成 CSV
df = pd.DataFrame(data)
df.to_csv('ptt_stock_10pages.csv', index=False, encoding='utf-8-sig')
print("已完成，存檔 ptt_stock_10pages.csv")
