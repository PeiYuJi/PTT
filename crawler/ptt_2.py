import requests
from bs4 import BeautifulSoup
import csv
import time

# 設定 headers，模擬瀏覽器行為
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'cookie': 'over18=1'
}

# PTT 股票版首頁
base_url = 'https://www.ptt.cc/bbs/Stock/'

# 儲存資料的列表
data = []

# 先抓取最新一頁的 index.html 以找出最末頁 index
response = requests.get(base_url + 'index.html', headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

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
                # 去掉推文內容
                for push in main_content.find_all('div', class_='push'):
                    push.extract()
                content = main_content.text.strip()
            else:
                content = '無內文'
            
            # 取得推文與噓文數量
            push_count = len(article_soup.find_all('span', class_='push-tag', text='推'))
            boo_count = len(article_soup.find_all('span', class_='push-tag', text='噓'))
            
            # 儲存資料
            data.append([title, date, content, push_count, boo_count])
    
    # 每頁抓取間隔，避免被封鎖
    time.sleep(1)

# 儲存為 CSV 檔案
with open('ptt_stock_articles_10pages.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['標題', '時間', '內文', '推文數量', '噓文數量'])
    writer.writerows(data)

print(f'資料已儲存為 ptt_stock_articles_10pages.csv，共 {len(data)} 篇文章')
