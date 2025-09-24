import requests
from bs4 import BeautifulSoup
import pandas as pd

# ========== 設定 ==========
url = 'https://www.ptt.cc/bbs/Gossiping/M.1694264017.A.22E.html'  # PTT 單篇文章網址
cookies = {'over18': '1'}  # 過 18 驗證
headers = {'User-Agent': 'Mozilla/5.0'}

# ========== 下載並解析網頁 ==========
res = requests.get(url, cookies=cookies, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# ========== 抓取標題與內文 ==========
main_content = soup.select_one('#main-content')

# 抓標題
title_tag = soup.find('span', class_='article-meta-tag', string='標題')
title = title_tag.find_next_sibling('span').text if title_tag else '無標題'

# 抓內文（排除 meta 資訊與推文）
for tag in main_content.find_all(['div', 'span']):
    tag.decompose()
article_text = main_content.text.strip()

# ========== 抓推文/噓文 ==========
push_tags = soup.find_all('div', class_='push')

push_list = []
boo_list = []

for push in push_tags:
    tag = push.find('span', class_='push-tag').text.strip()
    user = push.find('span', class_='push-userid').text.strip()
    content = push.find('span', class_='push-content').text.strip()[1:].strip()  # 去除開頭的冒號

    if tag == '推':
        push_list.append(f'{user}: {content}')
    elif tag == '噓':
        boo_list.append(f'{user}: {content}')

# ========== 放進 DataFrame ==========
data = {
    '標題': [title],
    '內文': [article_text],
    '推文': [push_list],
    '噓文': [boo_list]
}

df = pd.DataFrame(data)

print(df)
