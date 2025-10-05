import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 設定 headers，模擬瀏覽器行為
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'cookie': 'over18=1'
}

base_url = 'https://www.ptt.cc/bbs/Stock/'

articles_list = []

# 取得最新頁
index = requests.get(base_url + 'index.html', headers=headers)
soup = BeautifulSoup(index.text, 'html.parser')

btn_prev = soup.find('a', string='‹ 上頁')
if btn_prev:
    href = btn_prev['href']
    last_page_index = int(href.split('index')[1].split('.html')[0]) + 1
else:
    last_page_index = 1

# 抓取前10頁
for page_num in range(last_page_index, last_page_index - 2, -1):
    page_url = f'{base_url}index{page_num}.html' if page_num != last_page_index else base_url + 'index.html'
    print(f'抓取 {page_url}')
    
    res = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    articles = soup.find_all('div', class_='r-ent')
    
    for article in articles:
        title_tag = article.find('div', class_='title').find('a')
        date_tag = article.find('div', class_='date')
        print(article)
        if title_tag:
            title = title_tag.text.strip()
            link = 'https://www.ptt.cc' + title_tag['href']
            date = date_tag.text.strip()
            
            # 進入文章頁面
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            # 取得文章內文（排除推文）
            main_content = article_soup.find('div', id='main-content')
            if main_content:
                for push in main_content.find_all('div', class_='push'):
                    push.extract()  # 移除推文，留下純文章內容
                content = main_content.text.strip()
            else:
                content = '無內文'
            
            # 計算推、噓、箭頭數量
            comments = article_soup.select('div.push')    
            push_count = sum(1 for c in comments if c.find('span', class_='push-tag').text.strip() == '推')
            boo_count = sum(1 for c in comments if c.find('span', class_='push-tag').text.strip() == '噓')
            arrow_count = sum(1 for c in comments if c.find('span', class_='push-tag').text.strip() == '→')

            score = push_count - boo_count
            total_comments = push_count + boo_count + arrow_count
            
            # 整理到字典
            articles_list.append({
                '標題': title,
                '時間': date,
                '內文': content,
                '推文數量': push_count,
                '噓文數量': boo_count,
                '箭頭數量': arrow_count,
                '總留言數': total_comments,
                '推噓比': score,
                '連結': link
            })
    
    time.sleep(1)  # 避免被擋

# 存成 DataFrame
df = pd.DataFrame(articles_list)
df.to_csv('ptt_stock_10pages.csv', index=False, encoding='utf-8-sig')

print(f'資料已儲存為 ptt_stock_10pages.csv，共 {len(df)} 筆文章')
print(df.head())
