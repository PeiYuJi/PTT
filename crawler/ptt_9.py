import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 設定 headers，模擬瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'cookie': 'over18=1'
}

BASE_URL = "https://www.ptt.cc"
BOARD = "Stock"
PAGE_LIMIT = 1  # 前幾頁文章

data = []

def get_article_data(article_url):
    """抓文章內文與推噓文數量"""
    res = requests.get(article_url, headers=headers)
    art_soup = BeautifulSoup(res.text, 'html.parser')
    
    # 文章內文
    main_content = art_soup.find(id="main-content")
    for tag in main_content.find_all(['div', 'span'], class_=['article-metaline', 'article-metaline-right', 'push']):
        tag.decompose()
    content = main_content.text.strip()
    
    # 推噓文計數
    print(art_soup)
    pushes = art_soup.find_all('div', class_='push')
    push_count = sum(1 for p in pushes if '推' in p.find('span', class_='push-tag').text)
    boo_count  = sum(1 for p in pushes if '噓' in p.find('span', class_='push-tag').text)
    arrow_count = sum(1 for p in pushes if '→' in p.find('span', class_='push-tag').text)
    
    return content, push_count, boo_count, arrow_count

# 先抓列表頁
index_url = f"{BASE_URL}/bbs/{BOARD}/index.html"

for _ in range(PAGE_LIMIT):
    res = requests.get(index_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.find_all('div', class_='r-ent')
    
    for art in articles:
        try:
            title_tag = art.find('a')
            if not title_tag:  # 有些文章被刪除
                continue
            title = title_tag.text.strip()
            link = BASE_URL + title_tag['href']
            author = art.find('div', class_='author').text.strip()
            date = art.find('div', class_='date').text.strip()
            
            content, push_count, boo_count, arrow_count = get_article_data(link)
            
            data.append({
                'title': title,
                'author': author,
                'date': date,
                'content': content,
                'push': push_count,
                'boo': boo_count,
                'arrow': arrow_count
            })
            
            time.sleep(0.3)  # 避免太快被擋
        except Exception as e:
            print(f"抓取文章失敗: {e}")
    
    # 找上一頁連結
    prev_link = soup.find('a', string='‹ 上頁')
    if prev_link:
        index_url = BASE_URL + prev_link['href']
    else:
        break

# 存成 CSV
df = pd.DataFrame(data)
df.to_csv('ptt_stock_articles.csv', index=False, encoding='utf-8-sig')
print("已存成 ptt_stock_articles.csv")
