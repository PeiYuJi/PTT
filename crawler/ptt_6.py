import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 設定 headers，模擬瀏覽器行為
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'cookie': 'over18=1'
}

# PTT 股票版首頁
base_url = 'https://www.ptt.cc/bbs/Stock/'

# 儲存文章資料
articles_list = []

# 先抓取最新一頁的 index.html 以找出最末頁
index = requests.get(base_url + 'index.html', headers=headers)
soup = BeautifulSoup(index.text, 'html.parser')

# 找到上一頁按鈕的連結，取得最大頁數
btn_prev = soup.find('a', string='‹ 上頁')
if btn_prev:
    href = btn_prev['href']  # 例如 /bbs/Stock/index3770.html
    last_page_index = int(href.split('index')[1].split('.html')[0]) + 1
else:
    last_page_index = 1

# 抓取前10頁文章
for page_num in range(last_page_index, last_page_index - 10, -1):
    page_url = f'{base_url}index{page_num}.html' if page_num != last_page_index else base_url + 'index.html'
    print(f'抓取 {page_url}')
    
    res = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    articles = soup.find_all('div', class_='r-ent')
    
    for article in articles:
        title_tag = article.find('div', class_='title').find('a')
        date_tag = article.find('div', class_='date')
        
        if title_tag:
            title = title_tag.text.strip()
            link = 'https://www.ptt.cc' + title_tag['href']
            date = date_tag.text.strip()
            
            # 進入文章頁面
            article_response = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # 取得文章內文
            main_content = article_soup.find('div', id='main-content')
            if main_content:
                for push in main_content.find_all('div', class_='push'):
                    push.extract()
                content = main_content.text.strip()
            else:
                content = '無內文'
            
            # ✅ 取得推文、噓文、箭頭數量（抓含 push-tag 的所有 span）
            push_count = 0
            boo_count = 0
            arrow_count = 0
#            for tag in article_soup.find_all('span', class_=lambda x: x and 'push-tag' in x):
#                text = tag.text.strip()
#                if text.startswith('推'):
#                    push_count += 1
#                elif text.startswith('噓'):
#                    boo_count += 1
#                elif text.startswith('→'):
#                    arrow_count += 1
            
            for tag in article_soup.find_all('span', class_=lambda x: x and 'hl push-tag' in x):
                text = tag.text.replace('\xa0','').strip()  # 清理空格與特殊空白
                if text == '推':
                    push_count += 1
                elif text == '噓':
                    boo_count += 1
                elif text == '→':
                    arrow_count += 1           

            # 計算推噓比 & 總留言數
            score = push_count - boo_count
            total_comments = push_count + boo_count + arrow_count
            
            # 儲存資料
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
    
    # 每頁抓取間隔，避免被封鎖
    time.sleep(1)

# 轉成 DataFrame
df = pd.DataFrame(articles_list)

# 顯示前5筆
print(df.head())

# 存成 CSV
df.to_csv('ptt_stock_10pages.csv', index=False, encoding='utf-8-sig')
print(f'資料已儲存為 ptt_stock_10pages.csv，共 {len(df)} 筆文章')
